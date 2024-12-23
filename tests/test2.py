import os
import tempfile
import multiprocessing
import rasterio
import numpy as np
from time import sleep

def clip_and_store(task_queue, result_queue, temp_dir):
    """
    Worker process to clip rasters and store them in a temp folder.
    """
    while True:
        task = task_queue.get()
        if task == "STOP":
            break

        raster_path, clip_coords, buffer_size = task
        try:
            with rasterio.open(raster_path) as src:
                # Clip raster with given coordinates (add buffer if needed)
                window = rasterio.windows.from_bounds(
                    *clip_coords, src.transform
                ).buffer(buffer_size, buffer_size)

                # Read the clipped data
                clipped_image = src.read(window=window)

                # Save the clipped image in the temp folder
                temp_file_path = os.path.join(temp_dir, f"clipped_{os.path.basename(raster_path)}.npy")
                np.save(temp_file_path, clipped_image)

                # Notify main process of the result
                result_queue.put((raster_path, temp_file_path))
        except Exception as e:
            result_queue.put((raster_path, f"ERROR: {str(e)}"))

def main():
    # Setup
    raster_files = ["path_to_raster1.tif", "path_to_raster2.tif"]  # Example raster files
    clip_coords = (xmin, ymin, xmax, ymax)  # Define your bounding box
    buffer_size = 10  # Buffer size for clipping

    # Create a temporary folder for the buffer
    temp_dir = tempfile.mkdtemp()

    # Create queues for task communication
    task_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()

    # Start the buffer process
    buffer_process = multiprocessing.Process(target=clip_and_store, args=(task_queue, result_queue, temp_dir))
    buffer_process.start()

    # Send tasks to the buffer process
    for raster_path in raster_files:
        task_queue.put((raster_path, clip_coords, buffer_size))

    # Retrieve results
    for _ in raster_files:
        raster_path, temp_file_path = result_queue.get()
        if "ERROR" in temp_file_path:
            print(f"Error processing {raster_path}: {temp_file_path}")
        else:
            print(f"Clipped image stored at: {temp_file_path}")

    # Clean up
    task_queue.put("STOP")
    buffer_process.join()

    # Optionally delete the temp directory after use
    import shutil
    shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main()