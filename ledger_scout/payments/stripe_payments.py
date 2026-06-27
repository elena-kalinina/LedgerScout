"""Stripe payments — the agent really pays for premium datasets.

Each approved premium dataset is acquired by creating a real Stripe PaymentIntent
(test mode), which succeeds and shows up as a genuine charge in the dashboard. The
budget itself — and the decision to approve, reallocate, or escalate an over-budget
purchase — lives in the agent orchestration (Procurement + human gates), which is
where the multi-agent showcase belongs. Free/open datasets cost nothing and never
touch Stripe.

Two backends behind one `Wallet` interface:
  * StripePaymentWallet — real Stripe sandbox (LEDGERSCOUT_STRIPE_LIVE=1 + STRIPE_SECRET_KEY)
  * SimulatedWallet     — deterministic, offline, mirrors the same accept/decline logic

(We originally targeted Issuing virtual cards, but EU sandboxes can't fund the test
Issuing balance, so authorizations only ever declined. PaymentIntents give real,
successful payments with no funding step — see docs/DATA_SOURCES.md.)
"""
import os
from dataclasses import dataclass

from .. import config

# Stripe's shared test PaymentMethod — always succeeds in test mode.
TEST_PAYMENT_METHOD = "pm_card_visa"

# Demo safety: a live secret key would charge real money. Refuse unless explicitly
# overridden, so a stray sk_live_… in .env can't turn the demo into a real spend.
LIVE_KEY_OVERRIDE = "LEDGERSCOUT_ALLOW_LIVE_KEY"


def euros_to_cents(amount_eur):
    return int(round(float(amount_eur) * 100))


def cents_to_euros(amount_cents):
    return round(amount_cents / 100, 2)


@dataclass
class AuthResult:
    approved: bool
    amount_eur: float
    reason: str
    payment_id: str | None = None


def _secret_key():
    return os.getenv("STRIPE_SECRET_KEY", "")


def is_live_key():
    """True when the configured secret key is a LIVE key (real money)."""
    return _secret_key().startswith("sk_live_")


def assert_test_key():
    """Refuse to move real money during a demo unless explicitly overridden.

    Raises if STRIPE_SECRET_KEY is a live key (sk_live_…) and the override env var
    is not set, so an accidental live key can never trigger a real charge."""
    if is_live_key() and os.getenv(LIVE_KEY_OVERRIDE) != "1":
        raise RuntimeError(
            "Refusing to charge: STRIPE_SECRET_KEY is a LIVE key (sk_live_…), which would "
            "spend REAL money. Use a test key (sk_test_…) for the demo. If this is "
            f"intentional, set {LIVE_KEY_OVERRIDE}=1 to override."
        )


def live_enabled():
    """True when we should hit real Stripe (toggle on + a test secret key present).

    The toggle is read live (not cached at import) so a long-running server can flip it
    per run; falls back to the import-time config default when the env var is unset."""
    default = "1" if config.USE_REAL_STRIPE else "0"
    toggle = os.getenv("LEDGERSCOUT_STRIPE_LIVE", default) == "1"
    return toggle and _secret_key().startswith("sk_")


def _stripe():
    import stripe

    stripe.api_key = _secret_key()
    return stripe


def charge(amount_eur, label, currency=None):
    """Create and confirm a real (test-mode) PaymentIntent. Returns the PI object."""
    assert_test_key()
    currency = (currency or config.STRIPE_CURRENCY).lower()
    return _stripe().PaymentIntent.create(
        amount=euros_to_cents(amount_eur),
        currency=currency,
        payment_method=TEST_PAYMENT_METHOD,
        confirm=True,
        description=f"Ledger Scout dataset: {label}",
        automatic_payment_methods={"enabled": True, "allow_redirects": "never"},
        metadata={"dataset": label, "buyer": "ledger_scout_agent"},
    )


# --------------------------------------------------------------------------- #
# Wallet — what the Coordinator actually uses
# --------------------------------------------------------------------------- #
class Wallet:
    """A research budget with a spendable limit. authorize() returns an AuthResult.

    The limit is enforced here (the agents own the budget). Over-limit purchases are
    declined until the limit is raised (the human-approval / reallocation beat)."""

    def __init__(self, limit_eur):
        self.limit_eur = round(float(limit_eur), 2)
        self.spent_eur = 0.0

    @property
    def available_eur(self):
        return round(self.limit_eur - self.spent_eur, 2)

    def authorize(self, amount_eur, label=""):  # pragma: no cover - overridden
        raise NotImplementedError

    def raise_limit_to(self, new_limit_eur):
        self.limit_eur = round(float(new_limit_eur), 2)
        return self.limit_eur

    @property
    def backend(self):
        return self.__class__.__name__


class SimulatedWallet(Wallet):
    """Offline, deterministic: no network, mirrors the live accept/decline logic."""

    def __init__(self, limit_eur):
        super().__init__(limit_eur)
        self._seq = 0

    def authorize(self, amount_eur, label=""):
        amount_eur = round(float(amount_eur), 2)
        if amount_eur <= 0:
            return AuthResult(True, amount_eur, "free dataset — no charge", None)
        if self.spent_eur + amount_eur <= self.limit_eur + 1e-9:
            self.spent_eur = round(self.spent_eur + amount_eur, 2)
            self._seq += 1
            return AuthResult(True, amount_eur, "paid within budget", f"sim_pi_{self._seq:03d}")
        return AuthResult(
            False,
            amount_eur,
            f"declined: €{amount_eur:.0f} exceeds €{self.available_eur:.0f} left in budget",
            None,
        )


class StripePaymentWallet(Wallet):
    """Real Stripe sandbox: approved purchases become genuine succeeded charges."""

    def authorize(self, amount_eur, label=""):
        amount_eur = round(float(amount_eur), 2)
        if amount_eur <= 0:
            return AuthResult(True, amount_eur, "free dataset — no charge", None)
        # Budget gate is ours: don't spend real money beyond the approved limit.
        if self.spent_eur + amount_eur > self.limit_eur + 1e-9:
            return AuthResult(
                False,
                amount_eur,
                f"declined: €{amount_eur:.0f} exceeds €{self.available_eur:.0f} left in budget",
                None,
            )
        pi = charge(amount_eur, label or "dataset")
        approved = getattr(pi, "status", "") == "succeeded"
        if approved:
            self.spent_eur = round(self.spent_eur + amount_eur, 2)
            reason = f"paid €{amount_eur:.0f} via Stripe (PaymentIntent succeeded)"
        else:
            reason = f"Stripe PaymentIntent not completed (status={getattr(pi, 'status', '?')})"
        return AuthResult(approved, amount_eur, reason, getattr(pi, "id", None))


def get_wallet(limit_eur):
    """Live Stripe wallet when enabled + key present, else the offline simulator."""
    if live_enabled():
        assert_test_key()  # fail fast before the run if a live key is configured
        return StripePaymentWallet(limit_eur)
    return SimulatedWallet(limit_eur)
