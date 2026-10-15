import argparse,json,hashlib,os
from pathlib import Path


def line_score(line,seed):
    h=hashlib.sha256()
    h.update(seed.encode('utf8'))
    h.update(b'\0')
    h.update(line.rstrip('\n').encode('utf8'))
    return int.from_bytes(h.digest(),'big')/(1<<256)


def split_file(input_path,train_out,val_out,val_ratio,seed):
    if not 0<=val_ratio<=1:raise ValueError('val_ratio must be between 0 and 1')
    input_path=Path(input_path);train_out=Path(train_out);val_out=Path(val_out)
    train_out.parent.mkdir(parents=True,exist_ok=True);val_out.parent.mkdir(parents=True,exist_ok=True)
    train_count=0;val_count=0;total=0
    train_tmp=train_out.with_suffix(train_out.suffix+'.tmp')
    val_tmp=val_out.with_suffix(val_out.suffix+'.tmp')
    with open(input_path,encoding='utf8') as src, open(train_tmp,'w',encoding='utf8') as train, open(val_tmp,'w',encoding='utf8') as val:
        for line in src:
            if not line.endswith('\n'):line=line+'\n'
            total+=1
            if line_score(line,seed)<val_ratio:
                val.write(line);val_count+=1
            else:
                train.write(line);train_count+=1
    os.replace(train_tmp,train_out);os.replace(val_tmp,val_out)
    return {
        'input':str(input_path),
        'train_out':str(train_out),
        'val_out':str(val_out),
        'seed':seed,
        'val_ratio':val_ratio,
        'total_lines':total,
        'train_lines':train_count,
        'val_lines':val_count,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',required=True)
    p.add_argument('--train-out',required=True)
    p.add_argument('--val-out',required=True)
    p.add_argument('--val-ratio',type=float,default=0.1)
    p.add_argument('--seed',default='achitic')
    a=p.parse_args()
    print(json.dumps(split_file(a.input,a.train_out,a.val_out,a.val_ratio,a.seed),ensure_ascii=False,sort_keys=True))


if __name__=='__main__':main()
