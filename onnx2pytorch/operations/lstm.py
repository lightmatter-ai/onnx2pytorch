from torch import nn


class Wrapped1LayerLSTM(nn.Module):
    """Wraps a 1-layer nn.LSTM to match the API of an ONNX LSTM.

    As currently implemented, it expects the h_0/c_0 inputs as
    in PyTorch (as a tuple) but returns them separately.
    """

    def __init__(self, lstm_module: nn.LSTM):
        super().__init__()
        self.lstm = lstm_module

    def forward(self, input, h_0c_0=None):
        (h_0, c_0) = h_0c_0
        (seq_len, batch, input_size) = input.shape
        num_layers = 1
        num_directions = self.lstm.bidirectional + 1
        hidden_size = self.lstm.hidden_size
        output, (h_n, c_n) = self.lstm(input, (h_0, c_0))

        # Y has shape (seq_length, num_directions, batch_size, hidden_size)
        Y = output.view(seq_len, batch, num_directions, hidden_size).transpose(1, 2)
        # Y_h has shape (num_directions, batch_size, hidden_size)
        Y_h = h_n.view(num_layers, num_directions, batch, hidden_size).squeeze(0)
        # Y_c has shape (num_directions, batch_size, hidden_size)
        Y_c = c_n.view(num_layers, num_directions, batch, hidden_size).squeeze(0)
        return Y, Y_h, Y_c