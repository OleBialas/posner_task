import os
import time
import csv
import pandas as pd
import numpy as np
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import datetime

DATA_DIR = "data"
LEADERBOARD_FILE = "leaderboard.csv"

class ExperimentHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if not event.src_path.endswith('.csv'):
            return
        time.sleep(2) # Wait to ensure file written
        
        # Get the participant directory and ID
        participant_dir = os.path.dirname(event.src_path)
        participant_id = os.path.basename(participant_dir)
        
        # Process the participant data
        process_participant_data(participant_id, participant_dir)
        # Update the leaderboard display
        update_leaderboard_display()

def process_participant_data(participant_id, participant_dir):
    try:
        file_path = os.path.join(participant_dir, f"{participant_id}_data.csv")
        print(f"Processing file: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return
            
        df = pd.read_csv(file_path)
        
        # Print column names and first few rows for debugging
        print(f"Columns: {df.columns.tolist()}")
        print(f"First few rows:\n{df.head()}")
        
        # Calculate task performance
        avg_response_time = df['response_time'].mean()
        avg_response_time_valid = df[df['valid']==True]['response_time'].mean()
        avg_response_time_invalid = df[df['valid']==False]['response_time'].mean()
        response_time_difference = avg_response_time_invalid - avg_response_time_valid
        
        # Check if response column is boolean
        if df['response'].dtype != bool:
            print(f"Warning: 'response' column is not boolean, attempting to convert")
            # Try to convert to boolean if it's strings like 'True'/'False'
            try:
                if df['response'].dtype == object:  # string type
                    df['response'] = df['response'].map({'True': True, 'False': False})
                else:
                    df['response'] = df['response'].astype(bool)
            except Exception as e:
                print(f"Error converting response column: {e}")
        
        # Calculate accuracy
        accuracy = df['response'].mean()
        
        print(f"Calculated metrics for {participant_id}:")
        print(f"  Avg Response Time: {avg_response_time}")
        print(f"  Avg Response Time Valid: {avg_response_time_valid}")
        print(f"  Avg Response Time Invalid: {avg_response_time_invalid}")
        print(f"  Response Time Difference: {response_time_difference}")
        print(f"  Accuracy: {accuracy}")
        
        # Update leaderboard
        update_leaderboard(
            participant_id,
            avg_response_time,
            avg_response_time_valid,
            avg_response_time_invalid,
            response_time_difference,
            accuracy)
        
    except Exception as e:
        print(f"Error processing data for {participant_id}: {e}")
        import traceback
        traceback.print_exc()

def update_leaderboard(
        participant_id,
        avg_response_time,
        avg_response_time_valid,
        avg_response_time_invalid,
        response_time_difference,
        accuracy):
    # Create leaderboard file if it doesn't exist
    if not os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Participant', 'Response Time (s)', 'Response Time Valid Cues (s)', 
                            'Response Time Invalid Cues (s)', 'Response Time Difference (s)', 'Accuracy'])
    
    # Read existing leaderboard
    leaderboard = pd.read_csv(LEADERBOARD_FILE)
    
    # Check if participant already exists
    if participant_id in leaderboard['Participant'].values:
        # Update existing entry
        idx = leaderboard.index[leaderboard['Participant'] == participant_id].tolist()[0]
        leaderboard.at[idx, 'Response Time (s)'] = avg_response_time
        leaderboard.at[idx, 'Response Time Valid Cues (s)'] = avg_response_time_valid
        leaderboard.at[idx, 'Response Time Invalid Cues (s)'] = avg_response_time_invalid
        leaderboard.at[idx, 'Response Time Difference (s)'] = response_time_difference
        leaderboard.at[idx, 'Accuracy'] = accuracy
    else:
        # Add new entry
        new_row = pd.DataFrame({
            'Participant': [participant_id],
            'Response Time (s)': [avg_response_time],
            'Response Time Valid Cues (s)': [avg_response_time_valid],
            'Response Time Invalid Cues (s)': [avg_response_time_invalid],
            'Response Time Difference (s)': [response_time_difference],
            'Accuracy': [accuracy]
        })
        leaderboard = pd.concat([leaderboard, new_row], ignore_index=True)
    
    # Sort by response time (lower is better) - this is just the default sort
    leaderboard = leaderboard.sort_values('Response Time (s)')
    
    # Save updated leaderboard
    leaderboard.to_csv(LEADERBOARD_FILE, index=False)

def update_leaderboard_display():
    """Generate an HTML file to display the leaderboard"""
    if not os.path.exists(LEADERBOARD_FILE):
        return
    
    leaderboard = pd.read_csv(LEADERBOARD_FILE)
    
    # Format the data for display
    formatted_leaderboard = leaderboard.copy()
    formatted_leaderboard['Response Time (s)'] = formatted_leaderboard['Response Time (s)'].round(3)
    formatted_leaderboard['Response Time Valid Cues (s)'] = formatted_leaderboard['Response Time Valid Cues (s)'].round(3)
    formatted_leaderboard['Response Time Invalid Cues (s)'] = formatted_leaderboard['Response Time Invalid Cues (s)'].round(3)
    formatted_leaderboard['Response Time Difference (s)'] = formatted_leaderboard['Response Time Difference (s)'].round(3)
    formatted_leaderboard['Accuracy'] = (formatted_leaderboard['Accuracy'] * 100).round(1).astype(str) + '%'
    
    # Create HTML with interactive sorting
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Leaderboard</title>
        <meta http-equiv="refresh" content="10">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; text-align: center; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #4CAF50; color: white; cursor: pointer; }
            th:hover { background-color: #3e8e41; }
            tr:nth-child(even) { background-color: #f2f2f2; }
            tr:hover { background-color: #ddd; }
            .gold { background-color: gold !important; }
            .silver { background-color: silver !important; }
            .bronze { background-color: #cd7f32 !important; }
            .sort-icon::after { content: ""; margin-left: 5px; }
            .sort-asc::after { content: " ▲"; }
            .sort-desc::after { content: " ▼"; }
        </style>
    </head>
    <body>
        <h1>Experiment Leaderboard</h1>
        <p>Last updated: """ + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        <p>Click on any column header to sort the table by that column. Click again to reverse the sort order.</p>
        <table id="leaderboardTable">
            <thead>
                <tr>
                    <th data-sort="rank">Rank</th>
                    <th data-sort="participant">Participant</th>
                    <th data-sort="response-time" class="sort-asc">Response Time (s)</th>
                    <th data-sort="valid-cues">Response Time Valid Cues (s)</th>
                    <th data-sort="invalid-cues">Response Time Invalid Cues (s)</th>
                    <th data-sort="difference">Response Time Difference (s)</th>
                    <th data-sort="accuracy">Accuracy</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Default sort by response time
    formatted_leaderboard = formatted_leaderboard.sort_values('Response Time (s)')
    
    for i, (_, row) in enumerate(formatted_leaderboard.iterrows()):
        rank_class = ""
        if i == 0:
            rank_class = "gold"
        elif i == 1:
            rank_class = "silver"
        elif i == 2:
            rank_class = "bronze"
            
        # Store original numeric values as data attributes for proper sorting
        html += f"""
            <tr class="{rank_class}" 
                data-rank="{i+1}"
                data-response-time="{leaderboard.iloc[i]['Response Time (s)']}"
                data-valid-cues="{leaderboard.iloc[i]['Response Time Valid Cues (s)']}"
                data-invalid-cues="{leaderboard.iloc[i]['Response Time Invalid Cues (s)']}"
                data-difference="{leaderboard.iloc[i]['Response Time Difference (s)']}"
                data-accuracy="{leaderboard.iloc[i]['Accuracy']}">
                <td>{i+1}</td>
                <td>{row['Participant']}</td>
                <td>{row['Response Time (s)']}</td>
                <td>{row['Response Time Valid Cues (s)']}</td>
                <td>{row['Response Time Invalid Cues (s)']}</td>
                <td>{row['Response Time Difference (s)']}</td>
                <td>{row['Accuracy']}</td>
            </tr>
        """
    
    html += """
            </tbody>
        </table>

        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const table = document.getElementById('leaderboardTable');
                const headers = table.querySelectorAll('th');
                const tableBody = table.querySelector('tbody');
                const rows = tableBody.querySelectorAll('tr');
                
                // Current sort state
                let currentSort = {
                    column: 'response-time',
                    direction: 'asc'
                };
                
                // Function to sort table
                const sortTable = (column) => {
                    // Update sort direction
                    if (currentSort.column === column) {
                        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
                    } else {
                        currentSort.column = column;
                        currentSort.direction = 'asc';
                    }
                    
                    // Update header classes
                    headers.forEach(header => {
                        header.classList.remove('sort-asc', 'sort-desc');
                        if (header.getAttribute('data-sort') === column) {
                            header.classList.add(currentSort.direction === 'asc' ? 'sort-asc' : 'sort-desc');
                        }
                    });
                    
                    // Convert rows to array for sorting
                    const rowsArray = Array.from(rows);
                    
                    // Sort rows
                    rowsArray.sort((a, b) => {
                        let aValue = a.getAttribute('data-' + column);
                        let bValue = b.getAttribute('data-' + column);
                        
                        // Handle numeric values
                        if (!isNaN(aValue) && !isNaN(bValue)) {
                            aValue = parseFloat(aValue);
                            bValue = parseFloat(bValue);
                        }
                        
                        // Compare values
                        if (aValue < bValue) {
                            return currentSort.direction === 'asc' ? -1 : 1;
                        } else if (aValue > bValue) {
                            return currentSort.direction === 'asc' ? 1 : -1;
                        }
                        return 0;
                    });
                    
                    // Reorder rows in the table
                    rowsArray.forEach((row, index) => {
                        // Update rank
                        row.querySelector('td:first-child').textContent = index + 1;
                        
                        // Update medal classes
                        row.classList.remove('gold', 'silver', 'bronze');
                        if (index === 0) row.classList.add('gold');
                        else if (index === 1) row.classList.add('silver');
                        else if (index === 2) row.classList.add('bronze');
                        
                        // Append to table
                        tableBody.appendChild(row);
                    });
                };
                
                // Add click event listeners to headers
                headers.forEach(header => {
                    header.addEventListener('click', () => {
                        const column = header.getAttribute('data-sort');
                        if (column) {
                            sortTable(column);
                        }
                    });
                });
            });
        </script>
    </body>
    </html>
    """
    
    with open("leaderboard.html", "w") as f:
        f.write(html)

def check_existing_data():
    """Process existing data on startup"""
    if os.path.exists(DATA_DIR):
        for participant_folder in os.listdir(DATA_DIR):
            participant_dir = os.path.join(DATA_DIR, participant_folder)
            if os.path.isdir(participant_dir):
                # Process the participant data
                process_participant_data(participant_folder, participant_dir)
        
        # Update the display after processing all existing data
        update_leaderboard_display()

def main():
    # Create data directory if it doesn't exist
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # Process existing data first
    check_existing_data()
    
    # Set up file system observer
    event_handler = ExperimentHandler()
    observer = Observer()
    observer.schedule(event_handler, DATA_DIR, recursive=True)  # Changed back to recursive=True
    observer.start()
    
    print(f"Monitoring directory '{DATA_DIR}' for new CSV files...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
