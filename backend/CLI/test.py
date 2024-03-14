import keyboard

while True:
    key_event = keyboard.read_event(suppress=True)

    if key_event.event_type == keyboard.KEY_DOWN:
        key = key_event.name
        if key == 'enter':
            print('Enter is pressed')
        elif key == 'q':
            print('Quitting the program')
            break
        elif key == 's':
            print('Skipping the things')


import multiprocessing
import time
import keyboard

def key_listener(queue):
    while True:
        if keyboard.is_pressed('esc'):
            queue.put('esc')
            break

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

    # Wait for the display process to finish (since it contains the exit condition)
    display_process.join()

    # Wait for the key listener process to finish (optional, as it continuously checks)
    listener_process.join()
