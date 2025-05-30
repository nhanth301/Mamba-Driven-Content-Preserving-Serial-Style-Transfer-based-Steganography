import torch
import models.models_helper as models_helper
import models.MambaST as MambaST
import torch.nn as nn
import models.mamba as Mamba

def load_pretrained(args):
    vgg = models_helper.vgg
    vgg.load_state_dict(torch.load(args.vgg))
    vgg = nn.Sequential(*list(vgg.children())[:44])

    decoder = models_helper.decoder
    mamba = Mamba.Mamba(args=args)
    decoder_path = args.decoder_path
    mamba_path = args.mamba_path
    embedding_path = args.embedding_path
        
    embedding = models_helper.PatchEmbed()

    decoder.eval()
    mamba.eval()
    vgg.eval()
    from collections import OrderedDict
    new_state_dict = OrderedDict()
    state_dict = torch.load(decoder_path)
    for k, v in state_dict.items():
        namekey = k
        new_state_dict[namekey] = v
    decoder.load_state_dict(new_state_dict)

    new_state_dict = OrderedDict()
    state_dict = torch.load(mamba_path)
    model_dict = mamba.state_dict()

    for k, v in state_dict.items():
        if k in model_dict and v.shape == model_dict[k].shape:
            new_state_dict[k] = v
        else:
            print(f"Skip loading weight for: {k}")

    missing_keys = [k for k in model_dict if k not in new_state_dict]
    print(f"Missing keys in checkpoint: {len(missing_keys)}")

    model_dict.update(new_state_dict)
    mamba.load_state_dict(model_dict)

    new_state_dict = OrderedDict()
    state_dict = torch.load(embedding_path)
    for k, v in state_dict.items():
        namekey = k
        new_state_dict[namekey] = v
    embedding.load_state_dict(new_state_dict)

    network = MambaST.MambaST(vgg,decoder,embedding,mamba,args)
    
    print(f"Loaded Embedding checkpoints from {embedding_path}")
    print(f"Loaded Mamba checkpoints from {mamba_path}")
    print(f"Loaded CNN decoder checkpoints from {decoder_path}")
    return network