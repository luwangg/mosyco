from mosyco.reader import Reader
from mosyco.inspector import Inspector

def test_reader():
    reader = Reader()
    inspector = Inspector(reader.df.index)
    assert reader.df.index is inspector.df.index
    gen = reader.actual_value_gen()
    inspector.receive_actual_value(next(gen))
    assert int(inspector.df.PAcombi[0]) == 1049
