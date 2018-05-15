from keras.utils import vis_utils
from keras.models import load_model

model = load_model("first_model_full.h5")

vis_utils.plot_model(model, to_file="test.png", show_shapes=False, show_layer_names=True)
