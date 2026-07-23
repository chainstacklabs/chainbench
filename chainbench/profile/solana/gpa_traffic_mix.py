"""Solana getProgramAccounts profile: a single user class running all programs
as tasks weighted by production traffic, with filters and dataSlice.
"""
from chainbench.profile.solana._gpa import TRAFFIC_WEIGHTS, create_gpa_taskset_user

GetProgramAccounts = create_gpa_taskset_user(TRAFFIC_WEIGHTS)
