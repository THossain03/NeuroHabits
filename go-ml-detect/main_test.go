package main

import (
	"bytes"
	"encoding/json"
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestHealth(t *testing.T) {
	req := httptest.NewRequest("GET", "/health", nil)
	w := httptest.NewRecorder()
	healthHandler(w, req)
	resp := w.Result()
	if resp.StatusCode != 200 {
		t.Fatalf("expected 200, got %d", resp.StatusCode)
	}
}

func TestVersion(t *testing.T) {
	req := httptest.NewRequest("GET", "/version", nil)
	w := httptest.NewRecorder()
	versionHandler(w, req)
	resp := w.Result()
	if resp.StatusCode != 200 {
		t.Fatalf("expected 200, got %d", resp.StatusCode)
	}
}

func TestStats(t *testing.T) {
	req := httptest.NewRequest("GET", "/stats", nil)
	w := httptest.NewRecorder()
	statsHandler(w, req)
	resp := w.Result()
	if resp.StatusCode != 200 {
		t.Fatalf("expected 200, got %d", resp.StatusCode)
	}
}

func TestDetect(t *testing.T) {
	body := DetectRequest{
		Habits: []HabitRequest{{
			HabitID: "habit1",
			Logs: []HabitLog{{LoggedAt: "2024-06-01T08:00:00", Status: "COMPLETED"}},
		}},
	}
	b, _ := json.Marshal(body)
	req := httptest.NewRequest("POST", "/detect", bytes.NewReader(b))
	w := httptest.NewRecorder()
	detectHandler(w, req)
	resp := w.Result()
	if resp.StatusCode != 200 {
		t.Fatalf("expected 200, got %d", resp.StatusCode)
	}
	data, _ := ioutil.ReadAll(resp.Body)
	if !bytes.Contains(data, []byte("habit1")) {
		t.Fatalf("expected habit1 in response")
	}
} 