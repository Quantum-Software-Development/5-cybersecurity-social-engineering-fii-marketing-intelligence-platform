# Investor Intelligence Platform — Unix/Mac only
.PHONY: help install notebooks api dashboard clean
help:
	@echo "Commands: install | notebooks | api | dashboard | clean"
install:
	pip install -r requirements.txt
notebooks:
	jupyter notebook notebooks/
api:
	cd api && uvicorn app:app --reload --port 8000
dashboard:
	streamlit run dashboard/Home.py
clean:
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .ipynb_checkpoints spark-warehouse metastore_db derby.log 2>/dev/null || true
