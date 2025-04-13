import serial
import time

class GPSReader:
    def __init__(self, port="/dev/serial0", baud_rate=9600):
        self.port = port
        self.baud_rate = baud_rate

    def read_coordinates(self, attempts=100):
        """Đọc tọa độ GPS hợp lệ từ module."""
        try:
            with serial.Serial(self.port, self.baud_rate, timeout=1) as gps_serial:
                print("Đang đọc dữ liệu GPS...")
                for _ in range(attempts):
                    line = gps_serial.readline().decode('ascii', errors='replace').strip()

                    if line.startswith("$GPRMC"):
                        data = line.split(',')
                        if len(data) > 6 and data[2] == 'A':  # 'A' = data valid
                            raw_lat = data[3]
                            raw_long = data[5]
                            lat_dir = data[4]
                            long_dir = data[6]

                            lat = self.convert_to_degrees(raw_lat, lat_dir)
                            lon = self.convert_to_degrees(raw_long, long_dir)

                            if lat is not None and lon is not None:
                                print(f"Tọa độ: {lat:.6f}, {lon:.6f}")
                                return lat, lon

                    time.sleep(0.5)

                print("Không thể lấy được tọa độ GPS sau nhiều lần thử.")
                return None, None
        except KeyboardInterrupt:
            print("Dừng đọc GPS do bị ngắt.")
            return None, None

    def convert_to_degrees(self, raw_value, direction):
        """Chuyển định dạng NMEA sang độ thập phân."""
        if not raw_value or len(raw_value) < 4:
            return None

        degree_length = 2 if direction in ['N', 'S'] else 3
        try:
            degrees = float(raw_value[:degree_length])
            minutes = float(raw_value[degree_length:]) / 60.0
            result = degrees + minutes

            if direction in ['S', 'W']:
                result = -result

            return result
        except ValueError:
            return None

    def get_average_coordinates(self, samples=5):
        """Lấy tọa độ trung bình sau nhiều lần đọc."""
        coords = []
        for _ in range(samples):
            lat, lon = self.read_coordinates()
            if lat is not None and lon is not None:
                coords.append((lat, lon))
        if not coords:
            return None, None
        avg_lat = sum(c[0] for c in coords) / len(coords)
        avg_lon = sum(c[1] for c in coords) / len(coords)
        return avg_lat, avg_lon


if __name__ == "__main__":
    gps = GPSReader()
    gps.read_coordinates()
