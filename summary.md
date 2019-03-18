# Data cleaning
- use 'WIDS_Dataset_Full_Aug18_Jan19_Adjusted.csv'
- impute missing data for zone 1-3 based on rules defined according to pdf brief:
  - 97.36% fraction of samples have positional information for Zone1
  - 99.93% fraction of samples have positional information for Zone1 after imputation.
  - 97.33% fraction of samples have positional information for Zone2
  - 99.86% fraction of samples have positional information for Zone2 after imputation.
  - 97.34% fraction of samples have positional information for Zone3
  - 99.90% fraction of samples have positional information for Zone3 after imputation.

# Defect counts
![SKU_vs_Result_Type_Bin.png](figures/SKU_vs_Result_Type_Bin.png)
- SKU A001 has higher defect rate than the other SKUs. 

# Defect counts, details
![SKU_vs_Result_Type.png](figures/SKU_vs_Result_Type.png)
- SKU A001 mostly suffers from Defect_1.
- The other SKUs appear to have similar incidence rates for the different defects. Common root cause?
  - Defect_2 has the biggest incidence rate among these SKUs
  
# Defect financial impact
![SKU_vs_Result_Type_costs.png](figures/SKU_vs_Result_Type_costs.png)
- Scaled by cost, SKU A001 and B003 defects is a relatively smaller issue and X007 and Z009 relatively bigger. 

# Financial opportunities
![opportunities.png](figures/opportunities.png)

If we assume that the defects in the SKUs other than A001 have common root cause (based on SKU_vs_Result_Type showing
very similar incidence rates across these SKUs), our biggest opportunities are:
- Defect 2 across the non-A001 SKUs (~13 mill Euro)
- Defect_1 in A001 (~12 mill Euro)
- Defect_3 across the non-A001 SKUs (~5 mill Euro)
- Defect_4 across the non-A001 SKUs (~3.5 mill Euro)