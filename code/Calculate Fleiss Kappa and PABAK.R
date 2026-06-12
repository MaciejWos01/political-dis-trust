# Calculate Interrater Agreement for Political Trust Annotations by the three coders Y, E and M
# The labelling was categorical with three categories: trust(T), distrust (D), and no trust expression in text (NA)

# The interrater agreement will be calculated for the Uncompared Human Annotations, because these annotations were
# made completely independent without mutual influence between raters. 

library(tidyverse)
library(lpSolve)
library(irr)
library(survival)
library(epiR)


# Load 
human_annotations_uncompared <- read_csv("Human Annotations Uncompared.csv", na="",
                                         col_types = cols(id = col_character(),   # force id to be character
                                                          .default = col_guess()
                                         ))

# reshape so that there is a single "object" column
human_annotations_single_object <- human_annotations_uncompared %>% 
  mutate(object = coalesce(Y_O, E_O, M_O)) %>%
  select(
    id, text, object,
    Y = Y_L,
    E = E_L,
    M = M_L
  )

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# Calculate Fleiss' kappa ----------
# Note: Fleiss' kappa underestimates rater agreement when unequal categories

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
rater_labels <- human_annotations_single_object[,4:6]
kappam.fleiss(rater_labels, detail = TRUE)


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# Calculate the prevalence and bias corrected kappa statistic (PABAK)  ------------
# Note: in the epiR documentation I cannot find a solution for 3 raters and 3 categories
# Therefore, I wrote a function based on the formula

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

labels_only <- human_annotations_single_object %>% 
  select(-text)

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# Proportion of exact agreement across all 3 raters ---------

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

p_exact_agreement <- mean(apply(labels_only, 1, function(x) length(unique(x)) == 1))
p_exact_agreement

rater_labels[] <- lapply(rater_labels, factor, levels = c("D", "T", "NA"))
P_o <- mean(apply(rater_labels, 1, function(x) length(unique(x)) == 1))

# this is the observed proportion agreement P_o 

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# overall pabak ---------------

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

k <- length(levels(rater_labels$Y))  
PABAK <- (k * P_o - 1) / (k - 1)
PABAK

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# category specific pabak ---------------

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

pabak_by_category <- function(df) {
  # df: data.frame with 1 row per subject, columns = raters, factor or character
  
  # ensure character for convenience
  df_chr <- as.data.frame(lapply(df, as.character), stringsAsFactors = FALSE)
  cats <- sort(unique(unlist(df_chr)))
  
  out <- data.frame(
    category = cats,
    Po       = NA_real_,
    PABAK    = NA_real_,
    stringsAsFactors = FALSE
  )
  
  for (i in seq_along(cats)) {
    cati <- cats[i]
    
    ## For each subject and rater: 1 if category == cati, 0 otherwise
    bin <- as.data.frame(lapply(df_chr, function(x) as.integer(x == cati)))
    
    ## Subject-level agreement: do all raters give the same binary code?
    ## (all 1 = all rated cati, or all 0 = all rated "not cati")
    Po_i <- mean(apply(bin, 1, function(x) length(unique(x)) == 1))
    
    ## For binary (this category vs others), PABAK = 2 * Po - 1
    PABAK_i <- 2 * Po_i - 1
    
    out$Po[i]    <- Po_i
    out$PABAK[i] <- PABAK_i
  }
  
  out
}

pabak_by_category(rater_labels)

# Frequencies of given labels ---------
all_labels <- unlist(lapply(rater_labels, as.character))
freq_tab <- sort(table(all_labels), decreasing = TRUE)
freq_df <- data.frame(
  label = names(freq_tab),
  frequency = as.integer(freq_tab),
  stringsAsFactors = FALSE
)
freq_df
