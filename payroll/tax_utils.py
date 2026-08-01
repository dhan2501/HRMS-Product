"""
Income Tax (TDS) calculation utility.

Implements a simplified version of the Indian Income Tax slabs for the
Old Regime and New Regime (FY 2024-25 / AY 2025-26) so that the payroll
module can automatically work out the estimated annual tax and the
monthly TDS to deduct from an employee's salary package, based on the
tax regime chosen for that employee.

NOTE: This is a simplified statutory calculator meant for an HRMS demo/
internal payroll estimate. It does not account for marginal relief,
HRA exemption computation, surcharge for very high incomes, or every
possible deduction (80CCD, 80TTA, etc). For real-world statutory
compliance, the numbers should be reviewed by the finance/HR team.
"""

from decimal import Decimal, ROUND_HALF_UP

# Standard deduction available on salary income under each regime
NEW_REGIME_STANDARD_DEDUCTION = Decimal('75000')
OLD_REGIME_STANDARD_DEDUCTION = Decimal('50000')

# Section 80C cap (old regime only)
SECTION_80C_LIMIT = Decimal('150000')

# Health & Education Cess applied on the income tax amount
CESS_RATE = Decimal('0.04')

NEW_REGIME_SLABS = [
    (Decimal('300000'), Decimal('0.00')),
    (Decimal('700000'), Decimal('0.05')),
    (Decimal('1000000'), Decimal('0.10')),
    (Decimal('1200000'), Decimal('0.15')),
    (Decimal('1500000'), Decimal('0.20')),
    (None, Decimal('0.30')),
]

OLD_REGIME_SLABS = [
    (Decimal('250000'), Decimal('0.00')),
    (Decimal('500000'), Decimal('0.05')),
    (Decimal('1000000'), Decimal('0.20')),
    (None, Decimal('0.30')),
]

# Section 87A rebate: if net taxable income is within this limit,
# tax payable becomes NIL for that regime.
NEW_REGIME_REBATE_LIMIT = Decimal('700000')
OLD_REGIME_REBATE_LIMIT = Decimal('500000')


def _round(amount):
    return Decimal(amount).quantize(Decimal('1'), rounding=ROUND_HALF_UP)


def _slab_tax(taxable_income, slabs):
    """Apply progressive slab rates to the taxable income."""
    taxable_income = Decimal(taxable_income)
    if taxable_income <= 0:
        return Decimal('0')

    tax = Decimal('0')
    lower = Decimal('0')
    for upper, rate in slabs:
        if upper is None:
            tax += (taxable_income - lower) * rate
            break
        if taxable_income > upper:
            tax += (upper - lower) * rate
            lower = upper
        else:
            tax += (taxable_income - lower) * rate
            break
    return tax


def calculate_tax(regime, annual_gross, deduction_80c=0, deduction_80d=0,
                   professional_tax_annual=0):
    """
    Calculate the estimated annual income tax (incl. cess) for an
    employee, based on their chosen tax regime and salary package.

    Returns a dict with the full breakup so it can be shown to the
    admin (taxable income, slab tax, cess, rebate applied, total tax,
    monthly TDS).
    """
    annual_gross = Decimal(str(annual_gross or 0))
    deduction_80c = Decimal(str(deduction_80c or 0))
    deduction_80d = Decimal(str(deduction_80d or 0))
    professional_tax_annual = Decimal(str(professional_tax_annual or 0))

    if regime == 'old':
        standard_deduction = OLD_REGIME_STANDARD_DEDUCTION
        capped_80c = min(deduction_80c, SECTION_80C_LIMIT)
        taxable_income = (
            annual_gross - standard_deduction - professional_tax_annual
            - capped_80c - deduction_80d
        )
        taxable_income = max(taxable_income, Decimal('0'))
        slab_tax = _slab_tax(taxable_income, OLD_REGIME_SLABS)
        rebate_applied = taxable_income <= OLD_REGIME_REBATE_LIMIT
    else:
        regime = 'new'
        standard_deduction = NEW_REGIME_STANDARD_DEDUCTION
        capped_80c = Decimal('0')  # not allowed under new regime
        taxable_income = annual_gross - standard_deduction
        taxable_income = max(taxable_income, Decimal('0'))
        slab_tax = _slab_tax(taxable_income, NEW_REGIME_SLABS)
        rebate_applied = taxable_income <= NEW_REGIME_REBATE_LIMIT

    if rebate_applied:
        slab_tax = Decimal('0')

    cess = (slab_tax * CESS_RATE)
    total_tax = _round(slab_tax + cess)
    monthly_tds = _round(total_tax / 12)

    return {
        'regime': regime,
        'standard_deduction': standard_deduction,
        'deduction_80c_applied': capped_80c,
        'deduction_80d_applied': deduction_80d if regime == 'old' else Decimal('0'),
        'taxable_income': _round(taxable_income),
        'slab_tax': _round(slab_tax),
        'cess': _round(cess),
        'rebate_applied': rebate_applied,
        'total_annual_tax': total_tax,
        'monthly_tds': monthly_tds,
    }