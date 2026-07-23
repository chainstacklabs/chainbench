"""Solana getProgramAccounts profile: one user class per program, equal
weights, one request per user per second, with dataSlice but no filters.
"""
from locust import constant_pacing

from chainbench.profile.solana._gpa import EQUAL_WEIGHTS, create_gpa_users

globals().update(create_gpa_users(EQUAL_WEIGHTS, wait_time=constant_pacing(1), use_filters=False))
