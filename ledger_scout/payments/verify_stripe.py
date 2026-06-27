"""Prove the Stripe payment rail works end-to-end (sandbox / test mode).

Creates one real test-mode PaymentIntent so you can confirm connectivity and see a
succeeded charge in the dashboard. No funding, cardholder, or card needed.

    python3 -m ledger_scout.payments.verify_stripe              # charge €1.00
    python3 -m ledger_scout.payments.verify_stripe --amount 40

Requires STRIPE_SECRET_KEY (sk_test_...) in .env.
"""
import argparse

from . import stripe_payments as sp


def main():
    parser = argparse.ArgumentParser(description="Verify the Stripe payment rail.")
    parser.add_argument("--amount", type=float, default=1.0, help="charge amount in EUR")
    parser.add_argument("--label", default="connectivity check", help="dataset label / description")
    args = parser.parse_args()

    if not sp._secret_key().startswith("sk_"):
        raise SystemExit("STRIPE_SECRET_KEY (sk_test_...) not found in environment / .env")

    print(f"Creating a test PaymentIntent for €{args.amount:.2f} ...")
    pi = sp.charge(args.amount, args.label)
    print(f"  id:       {pi.id}")
    print(f"  status:   {pi.status}")
    print(f"  amount:   {sp.cents_to_euros(pi.amount)} {pi.currency.upper()}")
    if pi.status == "succeeded":
        print("Stripe payment rail is live. The agent can pay for datasets for real.")
    else:
        print("PaymentIntent did not succeed — check the dashboard / keys.")


if __name__ == "__main__":
    main()
