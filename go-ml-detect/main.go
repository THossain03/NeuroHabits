package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"runtime"
	"sync"
	"time"
)

// API Documentation:
// POST /detect: Batch habit prediction
// GET /health: Health check
// GET /version: Service version
// GET /stats: Service stats (uptime, goroutines)

type HabitLog struct {
	LoggedAt string `json:"LoggedAt"`
	Status   string `json:"Status"`
}

type HabitRequest struct {
	HabitID string     `json:"habit_id"`
	Logs    []HabitLog `json:"logs"`
}

type DetectRequest struct {
	Habits []HabitRequest `json:"habits"`
}

type Prediction struct {
	HabitID    string      `json:"habit_id"`
	Prediction interface{} `json:"prediction"`
}

type DetectResponse struct {
	Predictions []Prediction `json:"predictions"`
}

type Stats struct {
	Uptime      string `json:"uptime"`
	Goroutines  int    `json:"goroutines"`
	GoVersion   string `json:"go_version"`
	ServiceName string `json:"service_name"`
}

var (
	startTime = time.Now()
)

func detectHandler(w http.ResponseWriter, r *http.Request) {
	var req DetectRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}
	preds := make([]Prediction, len(req.Habits))
	var wg sync.WaitGroup
	for i, habit := range req.Habits {
		wg.Add(1)
		go func(i int, habit HabitRequest) {
			defer wg.Done()
			// Real concurrent prediction: count completed logs
			count := 0
			for _, log := range habit.Logs {
				if log.Status == "COMPLETED" {
					count++
				}
			}
			preds[i] = Prediction{
				HabitID:    habit.HabitID,
				Prediction: map[string]interface{}{"completed_count": count},
			}
		}(i, habit)
	}
	wg.Wait()
	resp := DetectResponse{Predictions: preds}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("ok"))
}

func versionHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("go-ml-detect v1.0.0"))
}

func statsHandler(w http.ResponseWriter, r *http.Request) {
	s := Stats{
		Uptime:      time.Since(startTime).String(),
		Goroutines:  runtime.NumGoroutine(),
		GoVersion:   runtime.Version(),
		ServiceName: "go-ml-detect",
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(s)
}

func main() {
	http.HandleFunc("/detect", detectHandler)
	http.HandleFunc("/health", healthHandler)
	http.HandleFunc("/version", versionHandler)
	http.HandleFunc("/stats", statsHandler)
	log.Println("Go ML detect service running on :9000")
	log.Fatal(http.ListenAndServe(":9000", nil))
} 