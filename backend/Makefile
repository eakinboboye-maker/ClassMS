install:
	pip install -r requirements.txt

migrate:
	alembic upgrade head

run:
	uvicorn app.main:app --reload

test:
	pytest
	
	
seed:
	python seed_data.py

manage-run:
	python manage.py runserver

manage-migrate:
	python manage.py migrate

manage-test:
	python manage.py test
	
	
seed-run:
	python seed_data.py && uvicorn app.main:app --reload

worker-expiry-formal:
	python -m app.workers.grading_jobs --expiry-check --assessment-type formal
	
demo-seed:
	python seed_demo_data.py

worker-loop:
	bash supervisor_worker.sh
	
root-readme-check:
	test -f ../README.md

frontend-all:
	cd ../frontend/teacher-dashboard && npm install && \
	cd ../exam-client && npm install
	
frontend-teacher:
	cd ../frontend/teacher-dashboard && npm install && npm run dev

frontend-exam:
	cd ../frontend/exam-client && npm install && npm run dev
