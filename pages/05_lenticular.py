# -*- coding: utf-8 -*-
"""Lenticular Analyzer - Self-contained Streamlit page."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.shared_ui import init_page, render_shared_sidebar
from pages._phenomenon_base import render_phenomenon_page
init_page(title="Lenticular Analyzer")
render_shared_sidebar()
render_phenomenon_page("lenticular")
