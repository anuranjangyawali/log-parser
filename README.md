# Usage

Make sure the script is executeable first:

```shell 
chmod +x ./logparser
```

By default, without any flags, it prints valid JSON logs to stdout.

```shell
./logparser
```
With -o [PATH] optional argument you can specify the directory to write the log files.

```shell
./logparser -o $HOME
```
With -f [program] logparser prints error logs of the specified program to stdout.

```shell
./logparser -f kernel
```

For help enter:

```shell
./logparser -h
```

