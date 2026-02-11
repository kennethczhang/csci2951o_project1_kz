#ifndef TIMER_H
#define TIMER_H

#include <chrono>

class Timer {
private:
  std::chrono::high_resolution_clock::time_point start_time;
  std::chrono::high_resolution_clock::time_point end_time;
  bool running;

public:
  Timer() : running(false) {}

  void start() {
    start_time = std::chrono::high_resolution_clock::now();
    running = true;
  }

  void stop() {
    if (running) {
      end_time = std::chrono::high_resolution_clock::now();
      running = false;
    }
  }

  double getTime() {
    std::chrono::duration<double> elapsed;
    if (running) {
      elapsed = std::chrono::high_resolution_clock::now() - start_time;
    } else {
      elapsed = end_time - start_time;
    }
    return elapsed.count();
  }
};

#endif // TIMER_H
