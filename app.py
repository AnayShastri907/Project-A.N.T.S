from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import os
import pandas as pd
from backend.backend import ProjectManagementApp  # Correct import path

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

project_app = ProjectManagementApp()

@app.route('/')
def loading_screen():
    return render_template('loading.html')

@app.route('/main')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        process_excel(filepath)
        session['filename'] = filename
        return redirect(url_for('display_excel', filename=filename))

@app.route('/display_excel/<filename>')
def display_excel(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_excel(filepath)

    # Exclude columns you don't want to display
    columns_to_exclude = [
        'Cost per Unit of resource0',
        'Cost per Unit of resource1',
        'Cost per Unit of resource2',
        'Cost per Unit of resource3',
        'Cost per Unit of resource4'
    ]
    df = df.drop(columns=columns_to_exclude, errors='ignore')  # Use errors='ignore' to avoid issues if columns don't exist

    # Convert the DataFrame to an HTML table
    table = df.to_html(classes='data', header="true", index=False)

    # Render the HTML page with the table
    return render_template('results.html', table=table)

@app.route('/generate_aoa')
def generate_aoa():
    # Extract relevant data for display
    filename = session.get('filename')
    if not filename:
        flash("No file uploaded", 'danger')
        return redirect(url_for('home'))
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_excel(filepath)

    # Select specific columns for display
    aoa_data = df[['Activity', 'Duration', 'Predecessors']].to_dict(orient='records')

    # Generate the AOA diagram
    project_app.generate_aoa('static/aoa_graph.png')
    return render_template('display_graph.html', graph_url=url_for('static', filename='aoa_graph.png'), data=aoa_data)

@app.route('/generate_aon')
def generate_aon():
    # Extract relevant data for display
    filename = session.get('filename')
    if not filename:
        flash("No file uploaded", 'danger')
        return redirect(url_for('home'))
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_excel(filepath)

    # Select specific columns for display
    aon_data = df[['Activity', 'Duration', 'Predecessors']].to_dict(orient='records')

    # Generate the AON diagram
    project_app.generate_aon('static/aon_graph.png')
    return render_template('display_graph.html', graph_url=url_for('static', filename='aon_graph.png'), data=aon_data)


@app.route('/generate_duration_vs_resources')
def generate_duration_vs_resources():
    project_app.plot_duration_vs_resources(before_smoothing=True)
    return redirect(url_for('display_duration_vs_resources'))

@app.route('/generate_gantt_chart')
def generate_gantt_chart():
    critical_path_data = project_app.calculate_critical_path()
    project_app.plot_sequence_of_events(critical_path_data['critical_path'], before_smoothing=True)
    return redirect(url_for('display_gantt_chart'))

@app.route('/generate_resource_smoothing', methods=['GET', 'POST'])
def generate_resource_smoothing():
    if request.method == 'POST':
        activity_name = request.form['activity']
        new_start_time = int(request.form['new_start_time'])

        try:
            message = project_app.adjust_non_critical_path_activity(activity_name, new_start_time)
            flash(message, 'success')
            # Regenerate the resource leveling Gantt chart with adjusted start times
            project_app.plot_resource_smoothing('static/resource_smoothing_gantt_chart.png')
        except ValueError as e:
            flash(str(e), 'danger')

    # Generate the resource leveling Gantt chart
    project_app.plot_resource_smoothing('static/resource_smoothing_gantt_chart.png')
    return render_template('display_resource_smoothing.html', graph_url=url_for('static', filename='resource_smoothing_gantt_chart.png'))

@app.route('/display_aoa')
def display_aoa():
    return render_template('display_graph.html', graph_url=url_for('static', filename='aoa_graph.png'))

@app.route('/display_aon')
def display_aon():
    return render_template('display_graph.html', graph_url=url_for('static', filename='aon_graph.png'))

@app.route('/display_duration_vs_resources')
def display_duration_vs_resources():
    return render_template('display_graph.html', graph_url=url_for('static', filename='duration_vs_resources.png'))

@app.route('/display_gantt_chart')
def display_gantt_chart():
    return render_template('gantt_chart.html', graph_url=url_for('static', filename='sequence_of_events.png'))

@app.route('/display_resource_smoothing')
def display_resource_smoothing():
    # Render the Gantt chart and provide the adjust activity form
    return render_template('display_resource_smoothing.html', graph_url=url_for('static', filename='resource_smoothing_gantt_chart.png'))

@app.route('/show_critical_path')
def show_critical_path():
    critical_path_data = project_app.calculate_critical_path()
    return render_template('critical_path.html', data=critical_path_data)

@app.route('/clear_session')
def clear_session():
    session.pop('filename', None)
    return redirect(url_for('home'))

@app.route('/adjust_activity', methods=['POST'])
def adjust_activity():
    activity_name = request.form['activity']
    new_start_time = int(request.form['new_start_time'])

    try:
        message = project_app.adjust_non_critical_path_activity(activity_name, new_start_time)
        flash(message, 'success')
        # Regenerate the resource leveling Gantt chart with adjusted start times
        project_app.plot_resource_smoothing('static/resource_smoothing_gantt_chart.png')
    except ValueError as e:
        flash(str(e), 'danger')

    return redirect(url_for('display_resource_smoothing'))

@app.route('/generate_s_curve', methods=['GET', 'POST'])
def generate_s_curve():
    if request.method == 'POST':
        # Input existing cash injections
        time_points = request.form.getlist('time_points[]')
        cash_injections = request.form.getlist('cash_injections[]')

        # Clear and update existing cash injections
        project_app.cash_injections.clear()
        for time_point, cash in zip(time_points, cash_injections):
            try:
                project_app.cash_injections[int(time_point)] = float(cash)
            except ValueError:
                continue

        # Input new cash injections
        new_time_points = request.form.getlist('new_time_points[]')
        new_cash_injections = request.form.getlist('new_cash_injections[]')

        for new_time_point, new_cash in zip(new_time_points, new_cash_injections):
            if new_time_point and new_cash:
                try:
                    project_app.cash_injections[int(new_time_point)] = float(new_cash)
                except ValueError:
                    pass  # Handle invalid inputs gracefully

        # Plot S-curve with updated cash injections
        project_app.plot_Scurve()
        return redirect(url_for('display_s_curve'))

    # Generate the initial S-curve
    project_app.plot_Scurve()
    return render_template('s_curve.html', cash_injections=project_app.cash_injections)

@app.route('/display_s_curve')
def display_s_curve():
    return render_template('display_graph.html', graph_url=url_for('static', filename='s_curve.png'))

@app.route('/adjust_crash_budget', methods=['POST'])
def adjust_crash_budget():
    crash_budget = request.form.get('crash_budget', type=float)

    if crash_budget is None or crash_budget <= 0:
        flash("Invalid budget! Please enter a positive number.", 'danger')
        return redirect(url_for('display_crashing'))

    # Apply the crash budget and regenerate the Gantt chart
    project_app.crash_activities_until_irreducible_path(crash_budget)
    critical_path_data = project_app.calculate_critical_path()
    project_app.plot_sequence_of_events(critical_path_data['critical_path'], before_smoothing=True)

    flash(f"Crash budget of ${crash_budget} applied.", 'success')
    return redirect(url_for('display_crashing'))

@app.route('/display_crashing')
def display_crashing():
    return render_template('display_crashing.html', graph_url=url_for('static', filename='sequence_of_events.png'))


def process_excel(filepath):
    df = pd.read_excel(filepath)
    df.columns = df.columns.str.strip()
    required_columns = ['Activity', 'Duration', 'Resources', 'Predecessors', 'Resources per unit cost', 'crash duration', 'crash cost', 'deadline']

    # Check for required columns
    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Missing required column: {column}")

    for index, row in df.iterrows():
        name = row['Activity'].strip()
        duration = int(row['Duration'])

        # Parse resources
        resources_str = str(row['Resources']).strip()
        resources = {}
        if resources_str.lower() != 'none':
            resource_items = resources_str.split(',')
            for item in resource_items:
                try:
                    k, v = item.split(':')
                    resources[k.strip()] = int(v.strip())
                except ValueError:
                    print(f"Skipping invalid resource entry: {item}")

        # Parse predecessors
        predecessors_str = str(row['Predecessors']).strip()
        predecessors = []
        if predecessors_str.lower() != 'none':
            predecessors = [pred.strip() for pred in predecessors_str.split(',')]

        # Parse cost per unit
        resources_per_unit_cost = {}
        for resource in resources:
            cost_col = f'Cost per Unit of {resource}'
            if cost_col in df.columns:
                resources_per_unit_cost[resource] = float(row[cost_col])
            else:
                # If cost is not specified, set a default value or
                # If cost is not specified, set a default value or raise a warning
                resources_per_unit_cost[resource] = 0
                print(f"Warning: Missing cost per unit for resource '{resource}' in activity '{name}'.")

        # Calculate total cost
        total_cost = sum(resources[resource] * resources_per_unit_cost.get(resource, 0) for resource in resources)

        # Debugging output to verify calculations
        print(f"Activity: {name}")
        print(f"Resources: {resources}")
        print(f"Resources per unit cost: {resources_per_unit_cost}")
        print(f"Total cost calculated: {total_cost}\n")

        crash_duration = int(row['crash duration'])
        crash_cost = float(row['crash cost'])
        deadline = int(row['deadline']) if not pd.isna(row['deadline']) else None

        # Add activity with validated data
        project_app.add_activity(name, duration, resources, predecessors, resources_per_unit_cost, total_cost, crash_duration, crash_cost, deadline)

if __name__ == '__main__':
    app.run(debug=True)
