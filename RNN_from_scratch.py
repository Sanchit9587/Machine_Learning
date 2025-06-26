import numpy as np

#This function assigns a unique value to each character which will help me to one hot encode it 
def mappings(short_string):
    char_ix = {}
    ix_char = {}
    index = 0
    list_of_indices = []
    for character in short_string:
        if character not in char_ix:
            char_ix[character] = index
            ix_char[index] = character
            index += 1
        list_of_indices.append(char_ix[character])
    return list_of_indices, char_ix, ix_char, len(char_ix)

#Takes the list of unique values and one hot encodes them returns array of the text as one hot encoded vecs
def one_hot_encoding(list_of_indices, unique):
    one_hot_array = []
    for i in list_of_indices:
        one_hot_vec = [0] * unique
        one_hot_vec[i] = 1
        one_hot_array.append(one_hot_vec)
    return np.array(one_hot_array)

#This is the input layer maths
def rnn_cell_forward(x_t, h_prev, W_xh, W_hh, b_h):
    h_t = np.tanh(np.dot(W_xh, x_t) + np.dot(W_hh, h_prev) + b_h)
    return h_t

#softmax func implementation
def softmax(output_layer):
    output_layer -= np.max(output_layer)
    exp_sum = np.sum(np.exp(output_layer))
    return np.exp(output_layer) / exp_sum

input_text = "The quick brown fox jumps over the lazy dog. This is a much longer test string meant to simulate a full paragraph, which should help train a small RNN to predict the next character using 90 percent of this input."

list_of_indices, char_ix, ix_char, vocab_size = mappings(input_text)
one_hot_array = one_hot_encoding(list_of_indices, vocab_size)
train_len = int(len(one_hot_array) * 0.9) #kept the training length as 90% of the input string


#initializing the variables needed
hidden_size = 8
np.random.seed(0)
W_xh = np.random.randn(hidden_size, vocab_size) * 0.01
W_hh = np.random.randn(hidden_size, hidden_size) * 0.01
b_h = np.zeros((hidden_size,))
W_yh = np.random.randn(vocab_size, hidden_size) * 0.01
b_y = np.zeros((vocab_size,))
learning_rate = 0.01
epochs = 100

#training the weigths and biases over multiple epochs 
for epoch in range(epochs):
    h_t = np.zeros((hidden_size,))
    loss = 0
    h_t_array = []
    prob_dist_array = []
    indices = []
    x_array = []

    #forward pass loop
    for t in range(train_len - 1):
        x_t = one_hot_array[t]
        x_array.append(x_t)
        h_t = rnn_cell_forward(x_t, h_t, W_xh, W_hh, b_h)
        h_t_array.append(h_t)
        y_t = np.dot(W_yh, h_t) + b_y
        prob_dist = softmax(y_t)
        prob_dist_array.append(prob_dist)
        next_index = list_of_indices[t + 1]
        loss += -np.log(prob_dist[next_index])
        indices.append(next_index)

    #initializing the gradient descent matrices 
    dW_xh = np.zeros_like(W_xh)
    dW_hh = np.zeros_like(W_hh)
    db_h  = np.zeros_like(b_h)
    dW_yh = np.zeros_like(W_yh)
    db_y  = np.zeros_like(b_y)
    dh_next = np.zeros((hidden_size,))

    #calculating them for each step
    for t in reversed(range(len(indices))):
        dy = prob_dist_array[t].copy()
        dy[indices[t]] -= 1
        dW_yh += np.outer(dy, h_t_array[t])
        db_y += dy
        dh = np.dot(W_yh.T, dy) + dh_next
        dh_raw = (1 - h_t_array[t] ** 2) * dh
        dW_xh += np.outer(dh_raw, x_array[t])
        dW_hh += np.outer(dh_raw, h_t_array[t - 1] if t > 0 else np.zeros_like(h_t))
        db_h += dh_raw
        dh_next = np.dot(W_hh.T, dh_raw)

    #updating the weigths and biases 
    W_xh -= learning_rate * dW_xh
    W_hh -= learning_rate * dW_hh
    b_h  -= learning_rate * db_h
    W_yh -= learning_rate * dW_yh
    b_y  -= learning_rate * db_y



# Final forward pass to get last h_t
#predicting the next character
h_t = np.zeros((hidden_size,))
for t in range(train_len - 1):
    x_t = one_hot_array[t]
    h_t = rnn_cell_forward(x_t, h_t, W_xh, W_hh, b_h)

x_last = one_hot_array[train_len - 1]
h_last = rnn_cell_forward(x_last, h_t, W_xh, W_hh, b_h)
y_pred = np.dot(W_yh, h_last) + b_y
p_pred = softmax(y_pred)
predicted_index = np.argmax(p_pred)
predicted_char = ix_char[predicted_index]

print("\nPredicted next character:", predicted_char)
