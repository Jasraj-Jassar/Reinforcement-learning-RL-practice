try:
    import tkinter as tk
except ImportError:
    tk = None


GRAPH_WIDTH = 560
GRAPH_HEIGHT = 340
PADDING_LEFT = 55
PADDING_RIGHT = 20
PADDING_TOP = 35
PADDING_BOTTOM = 55
MAX_HISTORY = 80


class TrainingGraph:
    def __init__(self):
        self.history = []
        self.best_model_score = 0
        self.available = False
        self.closed = False
        self.root = None
        self.canvas = None
        self.status = None

        if tk is None:
            return

        try:
            self.root = tk.Tk()
            self.root.title("Dino Training Progress")
            self.root.protocol("WM_DELETE_WINDOW", self.close)
            self.canvas = tk.Canvas(
                self.root,
                width=GRAPH_WIDTH,
                height=GRAPH_HEIGHT,
                bg="#f5f5f5",
                highlightthickness=0,
            )
            self.canvas.pack(fill="both", expand=True)
            self.status = tk.Label(
                self.root,
                text="Waiting for first generation...",
                anchor="w",
                bg="#eeeeee",
                fg="#222222",
                padx=10,
                pady=6,
            )
            self.status.pack(fill="x")
            self.available = True
            self.draw()
            self.tick()
        except tk.TclError:
            self.available = False

    def record_generation(
        self,
        generation,
        model_score,
        population_score,
        q_states,
        exploration_rate,
    ):
        self.best_model_score = max(self.best_model_score, model_score)
        self.history.append(
            {
                "generation": generation,
                "model_score": model_score,
                "best_model_score": self.best_model_score,
                "population_score": population_score,
                "q_states": q_states,
                "exploration_rate": exploration_rate,
            }
        )

        if len(self.history) > MAX_HISTORY:
            self.history = self.history[-MAX_HISTORY:]

        self.draw()
        self.tick()

    def tick(self):
        if not self.available or self.closed:
            return

        try:
            self.root.update_idletasks()
            self.root.update()
        except tk.TclError:
            self.available = False
            self.closed = True

    def close(self):
        if self.closed:
            return

        self.closed = True
        self.available = False

        if self.root is not None:
            try:
                self.root.destroy()
            except tk.TclError:
                pass

    def draw(self):
        if not self.available or self.closed:
            return

        self.canvas.delete("all")
        width = max(self.canvas.winfo_width(), GRAPH_WIDTH)
        height = max(self.canvas.winfo_height(), GRAPH_HEIGHT)
        plot_left = PADDING_LEFT
        plot_right = width - PADDING_RIGHT
        plot_top = PADDING_TOP
        plot_bottom = height - PADDING_BOTTOM

        self.canvas.create_text(
            plot_left,
            16,
            text="Blue model score by generation",
            anchor="w",
            fill="#222222",
            font=("Segoe UI", 12, "bold"),
        )
        self.canvas.create_line(plot_left, plot_top, plot_left, plot_bottom, fill="#777777")
        self.canvas.create_line(plot_left, plot_bottom, plot_right, plot_bottom, fill="#777777")

        if not self.history:
            self.canvas.create_text(
                width / 2,
                height / 2,
                text="A point appears after each generation ends",
                fill="#555555",
                font=("Segoe UI", 10),
            )
            return

        max_score = max(
            1,
            max(point["best_model_score"] for point in self.history),
            max(point["population_score"] for point in self.history),
        )
        self._draw_grid(plot_left, plot_right, plot_top, plot_bottom, max_score)
        self._draw_line(
            plot_left,
            plot_right,
            plot_top,
            plot_bottom,
            max_score,
            "population_score",
            "#777777",
        )
        self._draw_line(
            plot_left,
            plot_right,
            plot_top,
            plot_bottom,
            max_score,
            "model_score",
            "#d12a2a",
        )
        self._draw_line(
            plot_left,
            plot_right,
            plot_top,
            plot_bottom,
            max_score,
            "best_model_score",
            "#2675c9",
        )
        self._draw_legend(plot_right, plot_top)
        self._draw_status()

    def _point_xy(self, index, key, plot_left, plot_right, plot_top, plot_bottom, max_score):
        if len(self.history) == 1:
            x = plot_left
        else:
            x_step = (plot_right - plot_left) / (len(self.history) - 1)
            x = plot_left + index * x_step

        value = self.history[index][key]
        y = plot_bottom - (value / max_score) * (plot_bottom - plot_top)
        return x, y

    def _draw_line(self, plot_left, plot_right, plot_top, plot_bottom, max_score, key, color):
        points = [
            self._point_xy(index, key, plot_left, plot_right, plot_top, plot_bottom, max_score)
            for index in range(len(self.history))
        ]

        if len(points) == 1:
            x, y = points[0]
            self.canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill=color, outline=color)
            return

        flat_points = [coordinate for point in points for coordinate in point]
        self.canvas.create_line(*flat_points, fill=color, width=2, smooth=True)

        for x, y in points[-8:]:
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill=color, outline=color)

    def _draw_grid(self, plot_left, plot_right, plot_top, plot_bottom, max_score):
        for step in range(5):
            value = round(max_score * step / 4)
            y = plot_bottom - (step / 4) * (plot_bottom - plot_top)
            self.canvas.create_line(plot_left, y, plot_right, y, fill="#dddddd")
            self.canvas.create_text(
                plot_left - 8,
                y,
                text=str(value),
                anchor="e",
                fill="#555555",
                font=("Segoe UI", 8),
            )

        first_generation = self.history[0]["generation"]
        last_generation = self.history[-1]["generation"]
        self.canvas.create_text(
            plot_left,
            plot_bottom + 18,
            text=f"gen {first_generation}",
            anchor="w",
            fill="#555555",
            font=("Segoe UI", 8),
        )
        self.canvas.create_text(
            plot_right,
            plot_bottom + 18,
            text=f"gen {last_generation}",
            anchor="e",
            fill="#555555",
            font=("Segoe UI", 8),
        )

    def _draw_legend(self, plot_right, plot_top):
        self.canvas.create_line(
            plot_right - 190,
            plot_top - 14,
            plot_right - 170,
            plot_top - 14,
            fill="#777777",
            width=2,
        )
        self.canvas.create_text(
            plot_right - 165,
            plot_top - 14,
            text="population",
            anchor="w",
            fill="#333333",
            font=("Segoe UI", 8),
        )
        self.canvas.create_line(
            plot_right - 100,
            plot_top - 14,
            plot_right - 80,
            plot_top - 14,
            fill="#d12a2a",
            width=2,
        )
        self.canvas.create_text(
            plot_right - 75,
            plot_top - 14,
            text="blue",
            anchor="w",
            fill="#333333",
            font=("Segoe UI", 8),
        )
        self.canvas.create_line(
            plot_right - 40,
            plot_top - 14,
            plot_right - 20,
            plot_top - 14,
            fill="#2675c9",
            width=2,
        )
        self.canvas.create_text(
            plot_right - 15,
            plot_top - 14,
            text="best",
            anchor="w",
            fill="#333333",
            font=("Segoe UI", 8),
        )

    def _draw_status(self):
        last = self.history[-1]
        self.status.config(
            text=(
                f"gen {last['generation']} | "
                f"blue {last['model_score']} | "
                f"best blue {last['best_model_score']} | "
                f"population {last['population_score']} | "
                f"explore {last['exploration_rate']:.0%} | "
                f"q states {last['q_states']}"
            )
        )
