meta:
  id: uv_data
  endian: le
seq:
  - id: header
    type: header
  - id: object_count
    type: s4
    doc: The number of Blender objects with vertex data
  - id: objects
    type: object
    repeat: expr
    repeat-expr: object_count
types:
  header:
    doc: Provides info about which UV channels need to be read and written
    seq:
      - id: uv_inputs
        doc: How many UV channels need to be read
        type: s4
      - id: uv_input
        doc: UV channel indices that will be read from
        type: s4
        repeat: expr
        repeat-expr: uv_inputs
      - id: uv_outputs
        doc: How many UV channels need to be written
        type: s4
      - id: uv_output
        doc: UV channel indices that will be written to
        type: s4
        repeat: expr
        repeat-expr: uv_inputs
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
        type: uv_target
      - id: record_count
        type: s4
      - id: records
        type: record
        repeat: expr
        repeat-expr: record_count
  record:
    doc: A single attribute
    seq:
      - id: target_count
        doc: How many places this attribute needs to be written to
        type: s4
      - id: targets
        type: uv_target
        repeat: expr
        repeat-expr: target_count
      - id: vertex_count
        type: s4
      - id: data
        type: f4
        repeat: expr
        repeat-expr: target_count * vertex_count
  uv_target:
    doc: A single UV channel and component to read from or write to
    seq:
      - id: channel
        type: s4
      - id: component
        type: s4