import multiprocessing
import keyboard
import time

def key_listener(queue):
    keyboard.hook(lambda event: queue.put(event.name))

def display_characters(queue):
    while True:
        char = queue.get()
        print(f"Received: {char}")

        # Check if the character is 'esc' (exit condition)
        if char == 'esc':
            print("Exiting the program.")
            break

if __name__ == "__main__":
    # Create a multiprocessing queue for communication
    char_queue = multiprocessing.Queue()

    # Create processes for key listening and character display
    listener_process = multiprocessing.Process(target=key_listener, args=(char_queue,))
    display_process = multiprocessing.Process(target=display_characters, args=(char_queue,))

    # Start the processes
    listener_process.start()
    display_process.start()

    # Wait for the key listener process to finish
    listener_process.join()

    # Signal the display process to exit by putting 'esc' in the queue
    char_queue.put('esc')

    # Wait for the display process to finish
    display_process.join()
