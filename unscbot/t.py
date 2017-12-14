import torch
import math
from torch.autograd import Variable

# N is batch size; D_in is input dimension;
# H is hidden dimension; D_out is output dimension.
N, D_in, H1, H2, D_out = 64, 1000, 1000, 1000, 50


def f1(a, b):
    return a * 2.0 + b / 2.0


xs = []
ys = []
for i in range(0, 100, 10):
    for i2 in range(0, 100, 10):
        ax = [float(i), float(i2)]
        xs.append(ax)
        ys.append([f1(*ax)])

N = len(xs)
D_in = len(xs[0])
D_out = len(ys[0])
H1 = 2
H2 = H1

# Create random Tensors to hold inputs and outputs, and wrap them in Variables.
# x = Variable(torch.randn(N, D_in))
# y = Variable(torch.randn(N, D_out), requires_grad=False)

x = Variable(torch.FloatTensor(xs))
y = Variable(torch.FloatTensor(ys), requires_grad=False)

# Use the nn package to define our model as a sequence of layers. nn.Sequential
# is a Module which contains other Modules, and applies them in sequence to
# produce its output. Each Linear Module computes output from input using a
# linear function, and holds internal Variables for its weight and bias.
model = torch.nn.Sequential(
    torch.nn.Linear(D_in, H1),
    torch.nn.Sigmoid(),
    # torch.nn.ReLU(),
    torch.nn.Linear(H1, D_out),
    # torch.nn.Sigmoid(),
    #torch.nn.Linear(H2, D_out),
)

# The nn package also contains definitions of popular loss functions; in this
# case we will use Mean Squared Error (MSE) as our loss function.
loss_fn = torch.nn.MSELoss(size_average=False)

learning_rate = 1e-6
early_stop = 1
for t in range(100000):
    # Forward pass: compute predicted y by passing x to the model. Module objects
    # override the __call__ operator so you can call them like functions. When
    # doing so you pass a Variable of input data to the Module and it produces
    # a Variable of output data.
    y_pred = model(x)

    # Compute and print loss. We pass Variables containing the predicted and true
    # values of y, and the loss function returns a Variable containing the
    # loss.
    loss = loss_fn(y_pred, y)
    print(t, loss.data[0])

    if loss.data[0] < early_stop or math.isnan(loss.data[0]):
        break

    # Zero the gradients before running the backward pass.
    model.zero_grad()

    # Backward pass: compute gradient of the loss with respect to all the learnable
    # parameters of the model. Internally, the parameters of each Module are stored
    # in Variables with requires_grad=True, so this call will compute gradients for
    # all learnable parameters in the model.
    loss.backward()

    # Update the weights using gradient descent. Each parameter is a Variable, so
    # we can access its data and gradients like we did before.
    for param in model.parameters():
        param.data -= learning_rate * param.grad.data

y2s = model(x)
i = 0
for y2 in y2s:
    print(int(y2[0]), f1(*(xs[i])))
    i += 1

if 1:
    for param in model.parameters():
        print(param.data)
