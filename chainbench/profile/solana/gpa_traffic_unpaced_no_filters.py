"""Solana getProgramAccounts profile: one user class per program, weighted by
production traffic, with dataSlice but no filters. No pacing - each user
issues requests back to back.
"""
from chainbench.profile.solana._gpa import TRAFFIC_WEIGHTS, create_gpa_users

globals().update(create_gpa_users(TRAFFIC_WEIGHTS, use_filters=False))
