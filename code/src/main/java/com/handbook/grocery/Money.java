package com.handbook.grocery;

import java.math.*;
import java.net.http.*;
import java.nio.file.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.function.*;

/** An amount of money. Immutable; scale fixed at 2 so equals and compareTo agree (Ch 23). */
public record Money(BigDecimal amount, Currency currency) implements Comparable<Money> {
    public static final Currency INR = Currency.getInstance("INR");
    public static final Money ZERO = new Money(BigDecimal.ZERO, INR);

    public Money {
        Objects.requireNonNull(amount, "amount");
        Objects.requireNonNull(currency, "currency");
        amount = amount.setScale(2, RoundingMode.HALF_UP);
    }
    public static Money rupees(long rupees)       { return new Money(BigDecimal.valueOf(rupees), INR); }
    public static Money rupees(String rupees)     { return new Money(new BigDecimal(rupees), INR); }
    public static Money rupees(BigDecimal rupees) { return new Money(rupees, INR); }
    public static Money paise(long paise)         { return new Money(BigDecimal.valueOf(paise, 2), INR); }

    public Money plus(Money other)   { same(other); return new Money(amount.add(other.amount), currency); }
    public Money minus(Money other)  { same(other); return new Money(amount.subtract(other.amount), currency); }
    public Money times(long n)       { return new Money(amount.multiply(BigDecimal.valueOf(n)), currency); }
    public Money times(double f)     { return new Money(amount.multiply(BigDecimal.valueOf(f)), currency); }
    public Money minusPercent(int percent) {
        return new Money(amount.multiply(BigDecimal.valueOf(100 - percent)).divide(BigDecimal.valueOf(100)), currency);
    }
    public Money max(Money other)    { return compareTo(other) >= 0 ? this : other; }
    public Money min(Money other)    { return compareTo(other) <= 0 ? this : other; }
    public boolean isGreaterThan(Money other) { return compareTo(other) > 0; }
    public boolean isZero()          { return amount.signum() == 0; }
    public long paise()              { return amount.movePointRight(2).longValueExact(); }
    @Override public int compareTo(Money other) { same(other); return amount.compareTo(other.amount); }
    private void same(Money other) {
        if (!currency.equals(other.currency)) throw new IllegalArgumentException("currency mismatch");
    }
}
