meta:
  id: uv_data
  endian: le
seq:
  - id: version
    doc: Incremented every time a change is made. Starts at 1.
    type: s4
  - id: num_objects
    type: s4
    doc: The number of Blender objects with vertex data
  - id: objects
    type: object
    repeat: expr
    repeat-expr: num_objects
types:
  object:
    doc: A single Blender object
    seq:
      - id: name_length
        type: s4
      - id: name
        type: str
        size: name_length
        encoding: UTF-8
      - id: padding
        size: (4 - name_length) % 4
      - id: vertex_source
        doc: Where we stashed the vertex indices
        type: uv_address
      - id: num_records
        type: s4
      - id: records
        type: record
        repeat: expr
        repeat-expr: num_records
  record:
    doc: A single attribute
    seq:
      - id: name_length
        type: s4
      - id: name
        type: str
        size: name_length
        encoding: UTF-8
      - id: padding
        size: (4 - name_length) % 4
      - id: vertex_count
        type: s4
      - id: dimensions
        type: s4
      - id: data
        type: f4
        repeat: expr
        repeat-expr: vertex_count * dimensions
  uv_address:
    doc: A single UV channel and component
    seq:
      - id: channel
        type: s4
      - id: component
        type: s4