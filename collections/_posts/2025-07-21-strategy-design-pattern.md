---
layout: post
title: "Strategy Design Pattern in Python"
date: 2025-07-21
summary: "Replace growing if/else blocks with Strategy + composition for cleaner, extensible checkout code."
categories: [programming, python, design-patterns, lld]
permalink: strategy-design-pattern
---

* TOC
{:toc}

![Photo by Paulo Silva on Unsplash](https://miro.medium.com/v2/resize:fit:4800/format:webp/0*vnEUMYdjYE0l-ZWx)
{: .post-image }

> **Goal:** Replace growing `if/else` blocks with **Strategy + composition** so adding a new payment method doesn’t require editing existing logic.

---

## The problem: checkout payments with branching logic

You’re building a checkout system for an e-commerce site. Users can pay with Stripe or PayPal (and later: Card, Apple Pay, [UPI](https://en.wikipedia.org/wiki/Unified_Payments_Interface), etc.).

The business logic changes by payment method: fees differ, currency conversion may apply, and flows can vary.

A first attempt often looks like this:

```python
class Checkout:
    def __init__(self, payment_method):
        self.payment_method = payment_method

    def pay(self, amount):
        if self.payment_method == "stripe":
            fee = 1.5 + 0.03 * amount
            total = amount + fee
            print(f"Stripe: Charging ${total:.2f} (including fees: ${fee:.2f})")

        elif self.payment_method == "paypal":
            usd_amount = amount * 0.012  # fake conversion rate
            fee = 0.30
            total = usd_amount + fee
            print(f"PayPal: Charging ${total:.2f} USD (converted + ${fee:.2f} fee)")

        else:
            raise ValueError("Unsupported payment method")


if __name__ == "__main__":
    Checkout("stripe").pay(100)
    Checkout("paypal").pay(100)
````

---

## What goes wrong with this approach

The problem isn’t that the code “doesn’t work”—it’s that it **doesn’t scale**.

As soon as you add Apple Pay or UPI, the `if/else` block grows and becomes:

* **Harder to read**
* **Harder to test**
* **Easier to break** when you modify existing branches

### Design smells

* **High coupling:** `Checkout.pay()` knows too much about each gateway’s rules.
* **Low cohesion:** one method is orchestrating + implementing multiple behaviors (SRP violation).
* **OCP violation:**[^solid] every new gateway means editing `Checkout.pay()`.

> Every new branch = modify existing code = regression risk.

---

## A “natural” improvement: inheritance

A common refactor is to introduce a base type and one class per gateway:

```python
from abc import ABC, abstractmethod


class PaymentProcessor(ABC):
    @abstractmethod
    def pay(self, amount: float) -> None:
        ...


class StripeProcessor(PaymentProcessor):
    def pay(self, amount: float) -> None:
        fee = 1.5 + 0.03 * amount
        total = amount + fee
        print(f"Stripe: Charging ${total:.2f} (including fees: ${fee:.2f})")


class PayPalProcessor(PaymentProcessor):
    def pay(self, amount: float) -> None:
        usd_amount = amount * 0.012
        fee = 0.30
        total = usd_amount + fee
        print(f"PayPal: Charging ${total:.2f} USD (converted + ${fee:.2f} fee)")


class Checkout:
    def __init__(self, payment_processor: PaymentProcessor):
        self.payment_processor = payment_processor

    def pay(self, amount: float) -> None:
        self.payment_processor.pay(amount)


if __name__ == "__main__":
    Checkout(StripeProcessor()).pay(100)
    Checkout(PayPalProcessor()).pay(100)
```

This is better: `Checkout` depends on an interface, not concrete implementations.

---

## Why inheritance still breaks down in real systems

Real payment systems don’t stop at `pay(amount)`.

They include variations like:

* Cards: **network selection** (Visa, Mastercard, AmEx), 3DS, SCA flows
* Fees: flat + %, tiered, region-based
* Currency conversion and taxes
* Cross-cutting logic: discounts, fraud checks, promotions

If you try to model all of that in one base class, it becomes a “fat interface”:

```python
from abc import ABC, abstractmethod


class PaymentProcessor(ABC):
    @abstractmethod
    def pay(self, amount: float) -> None:
        ...

    @abstractmethod
    def authorise(self, amount: float) -> None:
        ...

    @abstractmethod
    def calc_fee(self, amount: float) -> float:
        ...

    @abstractmethod
    def convert_currency(self, amount: float) -> float:
        ...

    @abstractmethod
    def apply_discount(self, amount: float) -> float:
        ...

    @abstractmethod
    def choose_network(self) -> str:
        ...
```

Now you get:

* **ISP violation:** subclasses are forced to implement methods they don’t need.
* **Subclass explosion:** every combo becomes a class.
* **Back to OCP risk:** base class keeps changing.

A Stripe processor shouldn’t have to “choose a card network”—but this design forces it.

**ISP (Interface Segregation Principle):**[^isp] clients should not be forced to depend on methods they do not use.

---

## The strategy pattern: isolate what changes

![Strategy + composition diagram]({{ "/images/posts/strategy-pattern-1.png" | relative_url }})

### Step 1: Identify stable vs. changing parts

In our payment example:

* **Stable (Context):** the checkout flow (orchestration)
* **Changing (Strategies):** fee calculation, network selection, currency conversion, etc.

### Step 2: Create small interfaces for the varying parts

Keep interfaces small and focused:

```python
from abc import ABC, abstractmethod


class PaymentProcessor(ABC):
    @abstractmethod
    def pay(self, amount: float) -> None:
        ...


class NetworkSelector(ABC):
    @abstractmethod
    def choose_network(self) -> str:
        ...
```

### Why “program to an interface” matters[^gof]

Bad (calling concrete methods):

```python
network_selector = VisaNetwork()
network_selector.choose_visa()

network_selector = AmexNetwork()
network_selector.choose_amex()
```

Good (calling a shared contract):

```python
network_selector = VisaSelector()
network_selector.choose_network()

network_selector = AmexSelector()
network_selector.choose_network()
```

---

## Implement strategies

Concrete strategies do one job well:

```python
# Network selection strategies
class VisaSelector(NetworkSelector):
    def choose_network(self) -> str:
        return "Visa"


class AmexSelector(NetworkSelector):
    def choose_network(self) -> str:
        return "Amex"


class NoNetwork(NetworkSelector):
    def choose_network(self) -> str:
        return "N/A"


# Payment strategies
class StripeProcessor(PaymentProcessor):
    def pay(self, amount: float) -> None:
        fee = 1.5 + 0.03 * amount
        print(f"Stripe: Charging ${amount + fee:.2f}")


class PayPalProcessor(PaymentProcessor):
    def pay(self, amount: float) -> None:
        usd_amount = amount * 0.012
        fee = 0.30
        print(f"PayPal: Charging ${usd_amount + fee:.2f} USD")


class CardProcessor(PaymentProcessor):
    def __init__(self, network_selector: NetworkSelector):
        self.network_selector = network_selector

    def pay(self, amount: float) -> None:
        net = self.network_selector.choose_network()
        print(f"{net} card: charging ${amount:.2f}")
```

---

## Compose in the context (Checkout)

`Checkout` is the **Context**. It delegates work to the currently selected strategy.

```python
from typing import Optional


class Checkout:
    def __init__(self, payment_strategy: Optional[PaymentProcessor] = None):
        self._payment_strategy: Optional[PaymentProcessor] = None
        if payment_strategy is not None:
            self.payment_strategy = payment_strategy

    @property
    def payment_strategy(self) -> PaymentProcessor:
        if self._payment_strategy is None:
            raise ValueError("Payment strategy not set.")
        return self._payment_strategy

    @payment_strategy.setter
    def payment_strategy(self, strategy: PaymentProcessor) -> None:
        if not isinstance(strategy, PaymentProcessor):
            raise TypeError("payment_strategy must implement PaymentProcessor.")
        self._payment_strategy = strategy

    def pay(self, amount: float) -> None:
        self.payment_strategy.pay(amount)
```

Now strategy switching becomes a runtime decision:

```python
checkout = Checkout()

checkout.payment_strategy = StripeProcessor()
checkout.pay(100)

checkout.payment_strategy = CardProcessor(VisaSelector())
checkout.pay(50)
```

> Use constructor injection when the strategy is required and stable. Allow swapping only if your domain needs it (e.g., “user changes payment method before checkout submit”).

---

## Quick comparison table

| Approach               | Pros                               | Cons                               | Best for                             |
| ---------------------- | ---------------------------------- | ---------------------------------- | ------------------------------------ |
| `if/else` dispatch     | Simple to start                    | Grows messy, OCP breaks            | Tiny scripts, 2–3 stable cases       |
| Inheritance-only       | Polymorphism, cleaner `Checkout`   | Fat base class, subclass explosion | When variations are few & aligned    |
| Strategy + composition | Extensible, testable, OCP-friendly | More classes/objects               | Real systems with evolving behaviors |

---

## Extending the design

Want discounts, taxes, fraud checks?

Add more small interfaces and compose them:

* `DiscountPolicy.apply(amount) -> amount`
* `FeePolicy.fee(amount) -> fee`
* `CurrencyConverter.convert(amount) -> amount`
* `FraudCheck.verify(order) -> bool`

Each concern stays isolated, and you can mix-and-match.

---

## Conclusion

### When to use Strategy

Use it when you have multiple behaviors that:

* do the same *job* with different internal logic
* need to change independently over time
* should be selectable at runtime (user choice, region, config)
* are starting to create large `if/else` blocks

### When *not* to use Strategy

Skip it if:

* you have one behavior and it’s unlikely to change
* the abstraction adds more complexity than value

---

### Notes

[^solid]: Robert C. Martin, *Agile Software Development: Principles, Patterns, and Practices (Prentice Hall, 2002)*.
[^isp]: **Interface Segregation Principle (ISP):** keep interfaces small so implementers don’t inherit methods they don’t need.
[^gof]: Erich Gamma, Richard Helm, Ralph Johnson, and John Vlissides, *Design Patterns: Elements of Reusable Object-Oriented Software (Addison-Wesley, 1994)*