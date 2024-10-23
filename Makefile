run:
	# Navigate to the backend folder and run Uvicorn
	cd backend && uvicorn app:app --host 0.0.0.0 --port 8001 --reload &
	
	# Navigate to the frontend folder and run Streamlit
	cd frontend && streamlit run app.py
