"""Solana getProgramAccounts profile: one user class per program, weighted by
a realistic traffic mix, one request per user every 10s, with filters and dataSlice.
"""
from locust import constant_pacing

from chainbench.profile.solana._gpa import TRAFFIC_WEIGHTS, create_gpa_users

globals().update(create_gpa_users(TRAFFIC_WEIGHTS, wait_time=constant_pacing(10)))
