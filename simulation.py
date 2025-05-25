# simulation.py

class PageReplacement:
    def __init__(self, pages, frames):
        self.pages = pages
        self.frames = frames

    def simulate_fifo(self):
        memory = []
        hits = 0
        faults = 0
        per_step = []
        for page in self.pages:
            if page in memory:
                hits += 1
                per_step.append("hit")
            else:
                faults += 1
                if len(memory) < self.frames:
                    memory.append(page)
                else:
                    memory.pop(0)
                    memory.append(page)
                per_step.append("fault")
        return {"memory_state": memory, "hits": hits, "faults": faults, "per_step_result": per_step}

    def simulate_lru(self):
        memory = []
        hits = 0
        faults = 0
        per_step = []
        for page in self.pages:
            if page in memory:
                hits += 1
                memory.remove(page)
                memory.append(page)
                per_step.append("hit")
            else:
                faults += 1
                if len(memory) < self.frames:
                    memory.append(page)
                else:
                    memory.pop(0)
                    memory.append(page)
                per_step.append("fault")
        return {"memory_state": memory, "hits": hits, "faults": faults, "per_step_result": per_step}

    def simulate_optimal(self):
        memory = []
        hits = 0
        faults = 0
        per_step = []
        pages = self.pages
        frames = self.frames
        for i in range(len(pages)):
            page = pages[i]
            if page in memory:
                hits += 1
                per_step.append("hit")
            else:
                faults += 1
                if len(memory) < frames:
                    memory.append(page)
                else:
                    # Find page to replace
                    farthest = -1
                    page_to_remove = None
                    for m_page in memory:
                        try:
                            idx = pages[i+1:].index(m_page)
                        except ValueError:
                            idx = float('inf')
                        if idx > farthest:
                            farthest = idx
                            page_to_remove = m_page
                    memory.remove(page_to_remove)
                    memory.append(page)
                per_step.append("fault")
        return {"memory_state": memory, "hits": hits, "faults": faults, "per_step_result": per_step}
