meta:
  id: uv_data
  endian: le
seq:
  - id: object_count
    type: s4
    doc: The number of Blender objects with vertex data
  - id: objects
    type: object
    repeat: expr
    repeat-expr: object_count
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
      - id: source_uv_layer
        type: s4
      - id: source_uv_dimension
        type: s4
      - id: record_count
        type: s4
      - id: records
        type: record
        repeat: expr
        repeat-expr: record_count
  record:
    doc: A single attribute
    seq:
      - id: target_uv_layer
        type: s4
      - id: dimensions
        type: s4
      - id: vertex_count
        type: s4
      - id: data
        type: f4
        repeat: expr
        repeat-expr: dimensions * vertex_count