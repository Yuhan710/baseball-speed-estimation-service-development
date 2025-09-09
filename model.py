
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dropout, Input, Dense
from tensorflow.keras.layers import Conv2D, UpSampling2D, Concatenate, MaxPooling2D

def ballLineModel(img_rows=48, img_cols=48, channels=3, gf=32):
    img_rows = 48
    img_cols = 48
    channels = 3
    img_shape = (img_rows, img_cols, channels)

    gf = 32

    d = Input(img_shape)
    conv1 = Conv2D(gf, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(d)
    conv1 = Conv2D(gf, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv1)
    pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)
    conv2 = Conv2D(gf*2, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool1)
    conv2 = Conv2D(gf*2, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv2)
    pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)
    conv3 = Conv2D(gf*4, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool2)
    conv3 = Conv2D(gf*4, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv3)
    drop4 = Dropout(0.2)(conv3)
    pool3 = MaxPooling2D(pool_size=(2, 2))(drop4)
    conv4 = Conv2D(gf*8, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool3)
    conv4 = Conv2D(gf*8, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv4)
    drop5 = Dropout(0.2)(conv4)


    up7 = Conv2D(gf*4, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(drop5))
    merge7 = Concatenate()([drop4,up7])
    conv7 = Conv2D(gf*4, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge7)
    conv7 = Conv2D(gf*4, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv7)

    up8 = Conv2D(gf*2, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(conv7))
    merge8 = Concatenate()([conv2,up8])
    conv8 = Conv2D(gf*2, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge8)
    conv8 = Conv2D(gf*2, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv8)

    up9 = Conv2D(gf, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(conv8))
    merge9 = Concatenate()([conv1,up9])
    conv9 = Conv2D(gf, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge9)
    conv9 = Conv2D(gf, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv9)
    conv9 = Conv2D(3, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv9)
    output_img = Conv2D(3, 1, activation = 'sigmoid')(conv9)

    model = Model(inputs = d,outputs = output_img)

    return model