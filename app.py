from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

# Helper functions to simulate FIFO, LRU, Optimal algorithms per process

def simulate_fifo(ref_string, frames_count):
    memory = []
    hits = 0
    faults = 0
    per_step = []
    memory_state = []
    pointer = 0
    for page in ref_string:
        if page in memory:
            hits += 1
            per_step.append("hit")
        else:
            faults += 1
            if len(memory) < frames_count:
                memory.append(page)
            else:
                memory[pointer] = page
                pointer = (pointer + 1) % frames_count
            per_step.append("fault")
        memory_state.append(memory.copy())
    return {
        "memory_state": memory_state,
        "hits": hits,
        "faults": faults,
        "per_step_result": per_step
    }

def simulate_lru(ref_string, frames_count):
    memory = []
    hits = 0
    faults = 0
    per_step = []
    memory_state = []
    for page in ref_string:
        if page in memory:
            hits += 1
            per_step.append("hit")
            memory.remove(page)
            memory.append(page)
        else:
            faults += 1
            if len(memory) < frames_count:
                memory.append(page)
            else:
                memory.pop(0)
                memory.append(page)
            per_step.append("fault")
        memory_state.append(memory.copy())
    return {
        "memory_state": memory_state,
        "hits": hits,
        "faults": faults,
        "per_step_result": per_step
    }

def simulate_optimal(ref_string, frames_count):
    memory = []
    hits = 0
    faults = 0
    per_step = []
    memory_state = []
    for i in range(len(ref_string)):
        page = ref_string[i]
        if page in memory:
            hits += 1
            per_step.append("hit")
        else:
            faults += 1
            if len(memory) < frames_count:
                memory.append(page)
            else:
                # Find page not needed for longest time in future
                future = ref_string[i+1:]
                indexes = []
                for mem_page in memory:
                    if mem_page in future:
                        indexes.append(future.index(mem_page))
                    else:
                        indexes.append(float('inf'))
                to_replace = indexes.index(max(indexes))
                memory[to_replace] = page
            per_step.append("fault")
        memory_state.append(memory.copy())
    return {
        "memory_state": memory_state,
        "hits": hits,
        "faults": faults,
        "per_step_result": per_step
    }


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get input values
        num_processes = int(request.form.get('num_processes', 1))
        num_frames = int(request.form.get('num_frames', 3))
        algorithm = request.form.get('algorithm', 'FIFO').upper()
        
        # Reference strings per process
        reference_strings = []
        for i in range(1, num_processes+1):
            ref_str_raw = request.form.get(f'ref_str_p{i}', '')
            # parse input like "7,0,1,2,0,3"
            ref_list = [int(x.strip()) for x in ref_str_raw.replace(',', ' ').split() if x.strip().isdigit()]
            reference_strings.append(ref_list)

        # For each algorithm and each process, simulate
        simulation_results = {}
        for algo in ['FIFO', 'LRU', 'OPTIMAL']:
            simulation_results[algo] = []
            for ref_str in reference_strings:
                if algo == 'FIFO':
                    res = simulate_fifo(ref_str, num_frames)
                elif algo == 'LRU':
                    res = simulate_lru(ref_str, num_frames)
                else:
                    res = simulate_optimal(ref_str, num_frames)
                simulation_results[algo].append(res)
        
        # Now get results for selected algorithm to show output page
        selected_results = simulation_results[algorithm]

        # Calculate total hits and faults for summary (sum over all processes)
        total_hits = sum(r['hits'] for r in selected_results)
        total_faults = sum(r['faults'] for r in selected_results)

        # Recommended algorithm based on total faults (lowest faults)
        faults_per_algo = {algo: sum(r['faults'] for r in results) for algo, results in simulation_results.items()}
        recommended_algo = min(faults_per_algo, key=faults_per_algo.get)

        # Pass all needed info to template
        return render_template('result.html',
                               num_processes=num_processes,
                               num_frames=num_frames,
                               algorithm=algorithm,
                               recommended_algo=recommended_algo,
                               total_hits=total_hits,
                               total_faults=total_faults,
                               selected_results=selected_results,
                               simulation_results=simulation_results,
                               reference_strings=reference_strings)

    return render_template('index.html')
    

# API endpoint for dynamic chart data per process
@app.route('/chart-data/<algo>/<int:proc_id>')
def chart_data(algo, proc_id):
    # This route expects algo=FIFO,LRU,OPTIMAL and proc_id=0-based process index
    # In real, you might store simulation_results in session or DB; here just dummy or minimal example
    return jsonify({"message": "Implement storing/loading simulation results for chart"})

if __name__ == '__main__':
    app.run(debug=True)
