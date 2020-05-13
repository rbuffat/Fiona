from io import BytesIO
import fiona

from fiona import MemoryFile

schema = {'geometry': 'Point', 'properties': [('position', 'int')]}
records = [{'geometry': {'type': 'Point', 'coordinates': (0.0, float(i))}, 'properties': {'position': i}} for i in
           range(5)]
records2 = [{'geometry': {'type': 'Point', 'coordinates': (0.0, float(i))}, 'properties': {'position': i}} for i in
           range(5, 10)]

with fiona.open("/tmp/test.geojson", driver="GeoJSON")

# with MemoryFile() as memfile:
#
#     with MemoryFile() as memfile:
#         with memfile.open(driver="GeoJSON",
#                           schema=schema) as c:
#             c.writerecords(records)
#
#         memfile.seek(0)
#         print(memfile.read())
#
#         with BytesIO() as fout:
#             # fout.write("\n".encode())
#             with fiona.open(fout,
#                             'w',
#                             driver="GeoJSON",
#                             schema=schema) as c:
#                 c.writerecords(records2)
#             fout.seek(0)
#             data = fout.read()
#
#         memfile.write(data)
#         memfile.seek(0)
#         print("-------")
#         print(memfile.read())
#
#         with memfile.open(driver="GeoJSONSeq") as c:
#             record_positions = [int(f['properties']['position']) for f in c]
#             print(record_positions)
#             assert record_positions == list(range(5))
