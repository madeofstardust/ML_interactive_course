from plot_figure import *

def mse(y_true:np.array, y_pred:np.array) ->float:
  squared_difference = np.square(y_true-y_pred)
  return sum(squared_difference)/len(squared_difference)



x = [0, 1, 2, 3]
y_pred = [0.5, 0.1, 0.7, 0.6]
y_true = [1, 0.5, 0.8, 0.1]


#y_true= np.random.uniform(low=0.0, high=1.0, size=(4))
#y_pred= np.random.uniform(low=-0.0, high=0.8, size=(4))

print(mse(np.array(y_pred), np.array([0.5, 1, 2, 3])))
fig = produce_loss_plot(y_pred, y_true)
iplot(fig)

