# Hypothesetoetsen in R: dezelfde vragen als eti.sa.toetsen (zon, wind en batterij tegen de kapitaalkosten; daling
# van de capture rate). Alleen basis-R, geen pakketten nodig.
# Uitgevoerd op 18 november 2026 in R 4.6.0 (webR, R in de browser): dezelfde n, schattingen en aandelen als Python.
# De uitvoer en de vergelijking staan in resultaten/r_hypothesetoets_webr.txt.
# De p-waarden kunnen licht afwijken van de Python-uitkomst (andere benadering van de Wilcoxon-toets), en de
# Holm-correctie loopt hier over vier toetsen in plaats van zeven.
# Gebruik (vanuit de projectmap):  Rscript r/hypothesetoets.R

kapitaalkosten <- 0.05
gewone_jaren <- c(2023, 2024, 2025)

tech <- read.csv("powerbi/data/fact_tech_land.csv")
flex <- read.csv("powerbi/data/fact_flex_land.csv")
land <- read.csv("powerbi/data/fact_land_jaar.csv")

# Mediaan van de IRR per zone; een lege IRR (investering komt nooit terug) telt als -100%.
mediaan_per_zone <- function(d, kolom) {
  d[[kolom]][is.na(d[[kolom]])] <- -1
  aggregate(d[[kolom]], by = list(land = d$land), FUN = median)$x
}

# H0: de mediaan ligt op of onder de kapitaalkosten. H1: erboven.
toets_boven <- function(naam, x) {
  w <- wilcox.test(x, mu = kapitaalkosten, alternative = "greater", exact = FALSE)
  data.frame(toets = naam, n = length(x), schatting = median(x), aandeel_boven = mean(x > kapitaalkosten), p = w$p.value)
}

zon  <- mediaan_per_zone(subset(tech, technologie == "zon"  & jaar %in% gewone_jaren), "irr_merchant")
wind <- mediaan_per_zone(subset(tech, technologie == "wind" & jaar %in% gewone_jaren), "irr_merchant")
batterij <- mediaan_per_zone(subset(flex, uren_opslag == 2 & jaar %in% gewone_jaren), "irr_realistisch")
uit <- rbind(toets_boven("Zon: IRR boven kapitaalkosten", zon),
             toets_boven("Wind: IRR boven kapitaalkosten", wind),
             toets_boven("Batterij 2 uur: IRR boven kapitaalkosten", batterij))

# Gepaard per zone: is de capture rate van zon in 2025 lager dan in 2019? Waarden buiten 0..2 zijn rekenfouten.
land <- subset(land, capture_zon >= 0 & capture_zon <= 2 & jaar %in% c(2019, 2025))
breed <- reshape(land[, c("biedzone", "jaar", "capture_zon")], idvar = "biedzone", timevar = "jaar", direction = "wide")
breed <- na.omit(breed)
verschil <- breed$capture_zon.2025 - breed$capture_zon.2019
w <- wilcox.test(verschil, alternative = "less", exact = FALSE)
uit <- rbind(uit, data.frame(toets = "Capture rate zon 2025 lager dan 2019", n = length(verschil), schatting = mean(verschil),
                             aandeel_boven = mean(verschil > 0), p = w$p.value))

uit$p_holm <- p.adjust(uit$p, method = "holm")
uit$h0_verworpen <- uit$p_holm < 0.05
print(uit, digits = 3)
write.csv(uit, "powerbi/data/fact_toetsen_R_SA.csv", row.names = FALSE)
