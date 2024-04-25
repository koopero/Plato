import csv
import pcbnew
#
# Copy and paste this function into the KiCad scripting console.
# Make sure to adjust the csv_file_path variable to point to the CSV file you want to load.
#
def load_csv_and_update_pcb(csv_file_path):
    # Load the currently open PCB in the PCBnew editor
    board = pcbnew.GetBoard()

    # Open the CSV file and read the contents
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            part_name, x, y, orientation = row
            if part_name == 'Name':  # Skip the header row
                continue
            x = int(float(x) * 1000000)  # Convert mm to nm (nanometers)
            y = int(float(y) * 1000000)  # Convert mm to nm
            orientation = int(float(orientation))

            # Find the part on the board
            for footprint in board.GetFootprints():
                if footprint.GetReference() == part_name:
                    # Set the new position and orientation
                    position = pcbnew.VECTOR2I(x, y)
                    footprint.SetPosition(position)
                    # Convert orientation from degrees to 1/10th degrees and create EDA_ANGLE
                    footprint.SetOrientationDegrees(orientation)

    # Refresh to reflect changes in the editor
    pcbnew.Refresh()


# Example of usage within KiCad's scripting console
csv_file_path = 'YOUR_PROJECT_DIRECTORY/Plato_A1_LEDs.csv'  # Adjust the path as needed
load_csv_and_update_pcb(csv_file_path)
