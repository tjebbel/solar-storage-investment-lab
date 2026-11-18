"""All assumptions in one place. Solar NL: PBL SCE 2025 advice, ground-mounted PV (740 full-load hours,
EUR 449/kWp, EUR 15.7/kWp/yr O&M). Other values illustrative; see docs/methodology.md."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Assumptions:
    solar_mw: float = 20.0
    solar_full_load_hours: float = 740.0      # MWh per MW per year
    solar_capex_per_mw: float = 449_000.0
    solar_opex_per_mw: float = 15_700.0
    solar_degradation: float = 0.005
    solar_life: int = 25
    battery_mw: float = 10.0
    battery_hours: int = 2                      # 10 MW / 20 MWh
    battery_efficiency: float = 0.88            # round trip
    battery_capex_per_mwh: float = 300_000.0
    battery_opex_share: float = 0.02            # of capex per year
    battery_degradation: float = 0.02
    battery_life: int = 15
    discount_rate: float = 0.07
    debt_rate: float = 0.055
    dscr_target: float = 1.30
    hurdle_irr: float = 0.08
    revenue_sd_solar: float = 0.15
    revenue_sd_battery: float = 0.25
    simulations: int = 1000
    tax_rate: float = 0.258                     # Dutch CIT top rate
    battery_tariff_eur_mwh: float = 0.0          # grid tariff on charge and discharge (0 = behind solar meter)
