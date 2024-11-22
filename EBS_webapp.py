from flask import Flask, render_template, request, jsonify
from tasks import scrape_task  # Import the Celery task

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    # Get user inputs from the form
    search_query = request.form.get('search_query')
    filename = request.form.get('filename') or "output.csv"

    # Trigger the Celery task
    task = scrape_task.apply_async(args=[search_query, filename])
    
    # Return a response with the task ID
    return jsonify({
        "task_id": task.id,
        "status": "Task started. You can check the status using the /task-status/<task_id> endpoint."
    })

@app.route('/task-status/<task_id>', methods=['GET'])
def task_status(task_id):
    # Check the status of the Celery task
    from celery.result import AsyncResult
    result = AsyncResult(task_id)

    # Return task status information
    if result.state == "PENDING":
        response = {"status": "Pending..."}
    elif result.state == "SUCCESS":
        response = {"status": "Completed", "result": result.result}
    elif result.state == "FAILURE":
        response = {
            "status": "Failed",
            "error": str(result.info)  # Include error details if the task failed
        }
    else:
        response = {"status": result.state}

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
