"""Payments — the agent really pays for premium datasets via Stripe.

`get_wallet()` returns a live Stripe-backed wallet when LEDGERSCOUT_STRIPE_LIVE=1
(and STRIPE_SECRET_KEY is set), otherwise a deterministic local simulator that
mirrors the same budget/approval policy so the demo runs offline with no network.
"""
from .stripe_payments import AuthResult, Wallet, get_wallet, live_enabled

__all__ = ["AuthResult", "Wallet", "get_wallet", "live_enabled"]
