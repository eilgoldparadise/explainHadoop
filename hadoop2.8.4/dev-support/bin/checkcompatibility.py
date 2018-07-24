#!/usr/bin/env python
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# Script which checks Java API compatibility between two revisions of the Java client.
#脚本，它检查Java客户端的两个版本之间的Java API兼容性。
# Originally sourced from Apache Kudu, which was based on the compatibility checker from the Apache HBase project, but ported to Python for better readability.
#最初来源于Apache Kuu，它是基于Apache HBASE项目的兼容性检查器，但移植到Python以获得更好的可读性。
import logging
 #  输入  登录中
import os
#输入 操作系统
import re
#
import shutil
#输入 高级文件操作
import subprocess
#输入 子进程
import sys
#输入 系统文件（文件扩展名）
import urllib2
try:
  import argparse
  #   全面的参数处理库
except ImportError:
#除了 输入错误
  sys.stderr.write("Please install argparse, e.g. via `pip install argparse`.")
 #  系统文件.标准错误.写 “请安装arg解析，例如通过“pip install argparse”。”
 sys.exit(2)
#Python程序退出
# Various relative paths
 #各种相对路径
REPO_DIR = os.getcwd()
#获得当前路径
#在Python中可以使用os.getcwd()函数获得当前的路径。
#原型：
#os.getcwd()
#该函数不需要传递参数，它返回当前的目录。当前目录并不是指脚本所在的目录，而是所运行脚本的目录。
#>>>import  os
#>>>print  os.getcwd()
#D:\Python27
#这里的目录即是python的安装目录。若把上面的两行语句保存为getcwd.py，保存于f:\python\盘，运行后显示是f:\python
def check_output(*popenargs, **kwargs):
#
#call() 执行程序，并等待它完成

#def call(*popenargs, **kwargs):
#    return Popen(*popenargs, **kwargs).wait()
#check_call() 调用前面的call，如果返回值非零，则抛出异常

#def check_call(*popenargs, **kwargs):
#    retcode = call(*popenargs, **kwargs)
#    if retcode:
#        cmd = kwargs.get("args")
#        raise CalledProcessError(retcode, cmd)
#    return 0
#check_output() 执行程序，并返回其标准输出
#def check_output(*popenargs, **kwargs):
#    process = Popen(*popenargs, stdout=PIPE, **kwargs)
#    output, unused_err = process.communicate()
 #   retcode = process.poll()
 #   if retcode:
 #       cmd = kwargs.get("args")
 #       raise CalledProcessError(retcode, cmd, output=output)
 #   return output
#https://blog.csdn.net/dbzhang800/article/details/6879239
#现在还没学Python 暂时不到上面什么意思。。


  r"""Run command with arguments and return its output as a byte string.
  Backported from Python 2.7 as it's implemented as pure python on stdlib.
  >>> check_output(['/usr/bin/python', '--version'])
  Python 2.6.2
  """
  #这个应该是版本号、够老的版本，现在好像都3.6 了
  
  process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
  output, _ = process.communicate()
  retcode = process.poll()
  if retcode:
    cmd = kwargs.get("args")
    if cmd is None:
      cmd = popenargs[0]
    error = subprocess.CalledProcessError(retcode, cmd)
    error.output = output
    raise error
  return output
#check_output() 执行程序，并返回其标准输出
def get_repo_dir():

#repo 就是google 对git 的封装的一个小工具  （git： 版本管理的流行工具之一）
#repo 一般用来从代码源上 下载代码 
  """ Return the path to the top of the repo. """
  #将路径返回到repo的顶部
  
  dirname, _ = os.path.split(os.path.abspath(__file__))
  return os.path.join(dirname, "../..")
#
#os.path.abspath(__file__)返回的是.py文件的绝对路径（完整路径）
#os.path.dirname(__file__)返回的是.py文件的目录

#import os

#base_path = os.path.dirname(os.path.abspath(__file__))
#driver_path = os.path.abspath(__file__)

#print(base_path)
#print(driver_path)
#结果：
#C:\Test_framework\test
#C:\Test_framework\test\test.py
#
def get_scratch_dir():
  """ Return the path to the scratch dir that we build within. """
  #返回到我们内置的scratch 的DIR的路径。
  scratch_dir = os.path.join(get_repo_dir(), "target", "compat-check")
  #
  #os.path.join()函数用于路径拼接文件路径。 
#os.path.join()函数中可以传入多个路径：
#会从第一个以”/”开头的参数开始拼接，之前的参数全部丢弃。
#以上一种情况为先。在上一种情况确保情况下，若出现”./”开头的参数，会从”./”开头的参数的上一个参数开始拼接。
#import os
#print("1:",os.path.join('aaaa','/bbbb','ccccc.txt'))
#print("2:",os.path.join('/aaaa','/bbbb','/ccccc.txt'))
#print("3:",os.path.join('aaaa','./bbb','ccccc.txt'))
#输出为

#1: /bbbb\ccccc.txt
#2: /ccccc.txt
#3: aaaa\./bbb\ccccc.txt
  #https://blog.csdn.net/weixin_37895339/article/details/79185119
  if not os.path.exists(scratch_dir):
  #
  #.os.path.exists(path) 
#如果path存在，返回True；如果path不存在，返回False。 
 
#>>> os.path.exists('c:\\') 
#True 
#>>> os.path.exists('c:\\csv\\test.csv') 
#False 
  #https://www.cnblogs.com/wuxie1989/p/5623435.html
  
    os.makedirs(scratch_dir)
#
#os.makedirs() 方法用于递归创建目录。像 mkdir(), 但创建的所有intermediate-level文件夹需要包含子目录。
#语法
#makedirs()方法语法格式如下：
#os.makedirs(path, mode=0o777)
#参数
#path -- 需要递归创建的目录。
#mode -- 权限模式。
#返回值
#该方法没有返回值。
#实例
#以下实例演示了 makedirs() 方法的使用：
#!/usr/bin/python
# -*- coding: UTF-8 -*-
#import os, sys
# 创建的目录
#path = "/tmp/home/monthly/daily"
#os.makedirs( path, 0755 );
#print "路径被创建"
#执行以上程序输出结果为：
#路径被创建
#http://www.runoob.com/python/os-makedirs.html
  return scratch_dir

def get_java_acc_dir():
  """ Return the path where we check out the Java API Compliance Checker. """
  #返回检查Java API遵从检查程序的路径
  return os.path.join(get_repo_dir(), "target", "java-acc")
#os.path.join()函数用于路径拼接文件路径。

def clean_scratch_dir(scratch_dir):

  """ Clean up and re-create the scratch directory. """
  #清理并重新创建抓取目录
  if os.path.exists(scratch_dir):
  #如果路径存在
    logging.info("Removing scratch dir %s...", scratch_dir)
#清除痕迹
#默认情况下python的logging模块将日志打印到了标准输出中，且只显示了大于等于WARNING级别的日志，
#这说明默认的日志级别设置为WARNING（日志级别等级CRITICAL > ERROR > WARNING > INFO > DEBUG > NOTSET），
#默认的日志格式为:
#     日志级别：Logger名称：用户输出消息。
#python logging 替代print 输出内容到控制台和重定向到文件
    shutil.rmtree(scratch_dir)
#
#shutil.copyfile( src, dst)   #从源src复制到dst中去。 如果当前#的dst已存在的话就会被覆盖掉
#shutil.move( src, dst)  #移动文件或重命名
#shutil.copymode( src, dst) #只是会复制其权限其他的东西是不会被复制的
#shutil.copystat( src, dst) #复制权限、最后访问时间、最后修改时间
#shutil.copy( src, dst)  #复制一个文件到一个文件或一个目录
#shutil.copy2( src, dst)  #在copy上的基础上再复制文件最后访问时间与修改时间也复制过来了，类似于cp –p的东西
#shutil.copy2( src, dst)  #如果两个位置的文件系统是一样的话相当于是rename操作，只是改名；如果是不在相同的文件系统的话就是做move操作
#shutil.copytree( olddir, newdir, True/Flase) #把olddir拷贝一份newdir，如果第3个参数是True，则复制目录时将保持文件夹下的符号连接，如果第3个参数是False，则将在复制的目录下生成物理副本来替代符号连接
#shutil.rmtree( src )   #递归删除一个目录以及目录内的所有内容
#shutil.rmtree() #递归地删除文件

#如果存在以下树结构

# - user
#   - tester
#     - noob
#   - developer
#     - guru

#即 user 目录下存在多级子目录
#如果要递归删除user\tester 目录的内容，可使用shutil.rmtree()函数
#import shutil
#shutil.rmtree(r'user\tester') 
#mkdir -p foo/bar
#python
#import shutil
#shutil.rmtree('foo/bar')
#将会仅仅删除bar
#https://blog.csdn.net/jiandanjinxin/article/details/71489080
  logging.info("Creating empty scratch dir %s...", scratch_dir)
  #输出 创建空划线 dir
  os.makedirs(scratch_dir)
#os.makedirs() 方法用于递归创建目录

def checkout_java_tree(rev, path):
  """ Check out the Java source tree for the given revision into
  the given path. """
  #检查java源代码树中给定的修订到给定的路径。
  logging.info("Checking out %s in %s", rev, path)
  #输出检查
  os.makedirs(path)
  #创建目录
  # Extract java source
  #提取Java源代码
  subprocess.check_call(["bash", '-o', 'pipefail', "-c",
                         ("git archive --format=tar %s | " +
                          "tar -C \"%s\" -xf -") % (rev, path)],
                        cwd=get_repo_dir())
#
#subprocess.check_call()
#父进程等待子进程完成
#返回0
#检查退出信息，如果returncode不为0，则举出错误subprocess.CalledProcessError
#该对象包含有returncode属性，可用try…except…来检查
#
#从Python 2.4开始，Python引入subprocess模块来管理子进程，以取代一些旧模块的方法：
#如 os.system、os.spawn*、os.popen*、popen2.*、commands.*
#不但可以调用外部的命令作为子进程，而且可以连接到子进程的input/output/error管道，获取相关的返回信息
def get_git_hash(revname):
  """ Convert 'revname' to its SHA-1 hash. """
  #将“ReVNEX”转换为SHA-1哈希。
  return check_output(["git", "rev-parse", revname],
                      cwd=get_repo_dir()).strip()

def get_repo_name():
  """Get the name of the repo based on the git remote."""
  remotes = check_output(["git", "remote", "-v"],
                         cwd=get_repo_dir()).strip().split("\n")
#
#check_output
#subprocess.check_output(args, *, stdin = None, stderr = None, shell = False, universal_newlines = False)
#在子进程执行命令，以字符串形式返回执行结果的输出。如果子进程退出码不是0，抛出subprocess.CalledProcessError异常，异常的output字段包含错误输出：
#
  # Example output:
  # origin	https://github.com/apache/hadoop.git (fetch)
  # origin	https://github.com/apache/hadoop.git (push)
  remote_url = remotes[0].split("\t")[1].split(" ")[0]
  remote = remote_url.split("/")[-1]
#\t横向跳到下一制表符位置
#eg:String oid = oids.split(",")[0];
#string类中的split函数的功能是以给定字符串分隔字符串，返回一个分隔后的字符串数组
#所以这里oid得到的值是oids字符串中第一个,（逗号）之前的字符串。
#https://zhidao.baidu.com/question/2139836461980254748.html
  if remote.endswith(".git"):
    remote = remote[:-4]
#eg
#if f.endswith('.mhd') and f[:-4] not in config_training['black_list']:

#>>> l = list(range(10))
#>>> l
#[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
#>>> l[:-4]
#[0, 1, 2, 3, 4, 5]
#https://blog.csdn.net/qq_34690929/article/details/79924334

  return remote

def build_tree(java_path):
  """ Run the Java build within 'path'. """
  #在“PATH”中运行Java BUILD
  logging.info("Building in %s...", java_path)
  #打印 创建中 Java——path路径
  subprocess.check_call(["mvn", "-DskipTests", "-Dmaven.javadoc.skip=true",
                         "package"],
                        cwd=java_path)


def checkout_java_acc(force):
  """
  Check out the Java API Compliance Checker. If 'force' is true, will
  re-download even if the directory exists.
  """
  #检查Java API符合性检查程序。如果“强制”是真的，即使目录存在，也会重新下载。
  acc_dir = get_java_acc_dir()
  
  if os.path.exists(acc_dir):
    logging.info("Java ACC is already downloaded.")
    #输出 已经下载了Java ACC。
    if not force:
    
      return
    logging.info("Forcing re-download.")
    #输出 强制重新下载。
    shutil.rmtree(acc_dir)
#shutil.rmtree() #递归地删除文件
  logging.info("Downloading Java ACC...")
#下载Java ACC
  url = "https://github.com/lvc/japi-compliance-checker/archive/1.8.tar.gz"
  
  scratch_dir = get_scratch_dir()
  #调用函数
  path = os.path.join(scratch_dir, os.path.basename(url))
  #上面有解释
  jacc = urllib2.urlopen(url)
#
#urllib2是一个标准库，安装python之后就自带了，并且只在于python2中
#在python3中，已经把urllib，urllib2等的合并为一个包urllib了。
#Urllib2是用于获取URLs(统一资源定位符)的一个Python模块。它以urlopen函数的形式提供了非常简单的接口。
#能够使用各种不同的协议来获取网址。它还提供一个稍微复杂的接口用于处理常见的情况：
#如基本身份验证、cookies、proxies(代理)等。这些是由handlers和openers对象提供
#获取URLs
#简单的使用urllib2如下：
#    import urllib2
#    response = urllib2.urlopen('http://python.org')
#    html = response.read()
#    print html
#可以看到请求的网页已经被打印出来了。使用urllib2就是如此简单。
#(可使用'ftp:'、'file'代替'http:')
#HTTP是基于请求和响应---客户端发出请求和服务器端发送响应。Urllib2 对应Request对象表示你做出HTTP请求，最简单的形式，创建一个指定要获取的网址的Request对象。这个Request对象调用urlopen，返回URL请求的Response对象。Response对象是一个类似于文件对象，你可以在Response中使用 .read()。
#    import urllib2
#    req = urllib2.Request('http://python.org')
#    response = urllib2.urlopen(req)
#    the_page = response.read()
#    print the_page
#urlib2可以使用相同Request接口来处理所有URL方案，例如，你可以创建一个FTP请求：
#    req = urllib2.Request('ftp://example.com/')
#在HTTP协议中，Request对象有两个额外的事情可以做，第一，你可以通过将数据发送到服务器；
#第二，你可以通过数据的额外的信息(metadata)或请求到服务器本身，这个信息是发送HTTP'headers'。
#https://www.cnblogs.com/billyzh/p/5819957.html

  with open(path, 'wb') as w:
    w.write(jacc.read())
#不到什么意思 可能是读写？
  subprocess.check_call(["tar", "xzf", path],
                        cwd=scratch_dir)
#上面有
  shutil.move(os.path.join(scratch_dir, "japi-compliance-checker-1.8"),
              os.path.join(acc_dir))
#shutil.move( src, dst)  #移动文件或重命名

def find_jars(path):
  """ Return a list of jars within 'path' to be checked for compatibility. """ 
  #返回“路径”内的JAR列表，以检查兼容性。
  all_jars = set(check_output(["find", path, "-name", "*.jar"]).splitlines())
  #
  #Python splitlines()方法
#Python splitlines() 按照行('\r', '\r\n', \n')分隔，
#返回一个包含各行作为元素的列表，如果参数 keepends 为 False，不包含换行符，如果为 True，则保留换行符。
#语法
#splitlines()方法语法：
#str.splitlines([keepends])
#参数
#keepends -- 在输出结果里是否保留换行符('\r', '\r\n', \n')，默认为 False，不包含换行符，如果为 True，则保留换行符。
#返回值
#返回一个包含各行作为元素的列表。
#实例
#以下实例展示了splitlines()函数的使用方法：
#实例(Python 2.0+)
#!/usr/bin/python
#str1 = 'ab c\n\nde fg\rkl\r\n'
#print str1.splitlines();
#str2 = 'ab c\n\nde fg\rkl\r\n'
#print str2.splitlines(True)
#以上实例输出结果如下：
#['ab c', '', 'de fg', 'kl']
#['ab c\n', '\n', 'de fg\r', 'kl\r\n']
#http://www.runoob.com/python/att-string-splitlines.html

  return [j for j in all_jars if (
      "-tests" not in j and
      "-sources" not in j and
      "-with-dependencies" not in j)]

def write_xml_file(path, version, jars):
#写xml文件 路径 版本 ，jars
  """Write the XML manifest file for JACC."""
  #为JACC编写XML清单文件。
  with open(path, "wt") as f:
    f.write("<version>" + version + "</version>\n")
    f.write("<archives>")
    for j in jars:
      f.write(j + "\n")
    f.write("</archives>")
#archives -存档
def run_java_acc(src_name, src_jars, dst_name, dst_jars, annotations):
# annotations  注解
  """ Run the compliance checker to compare 'src' and 'dst'. """
  #运行符合性检查器比较“SRC”和“DST”
  logging.info("Will check compatibility between original jars:\n\t%s\n" +
               "and new jars:\n\t%s",
               "\n\t".join(src_jars),
               "\n\t".join(dst_jars))
#输出 将检查原始点之间的兼容性
  java_acc_path = os.path.join(get_java_acc_dir(), "japi-compliance-checker.pl")

  src_xml_path = os.path.join(get_scratch_dir(), "src.xml")
  dst_xml_path = os.path.join(get_scratch_dir(), "dst.xml")
  write_xml_file(src_xml_path, src_name, src_jars)
  write_xml_file(dst_xml_path, dst_name, dst_jars)

  out_path = os.path.join(get_scratch_dir(), "report.html")
#各种拼接 上面有解释
  args = ["perl", java_acc_path,
          "-l", get_repo_name(),
          "-d1", src_xml_path,
          "-d2", dst_xml_path,
          "-report-path", out_path]
#这代码先解释到这 等我学py再解释下，那时能更靠谱点
  if annotations is not None:
    annotations_path = os.path.join(get_scratch_dir(), "annotations.txt")
    with file(annotations_path, "w") as f:
      for ann in annotations:
        print >>f, ann
    args += ["-annotations-list", annotations_path]

  subprocess.check_call(args)

def filter_jars(jars, include_filters, exclude_filters):
  """Filter the list of JARs based on include and exclude filters."""
  filtered = []
  # Apply include filters
  for j in jars:
    found = False
    basename = os.path.basename(j)
    for f in include_filters:
      if f.match(basename):
        found = True
        break
    if found:
      filtered += [j]
    else:
      logging.debug("Ignoring JAR %s", j)
  # Apply exclude filters
  exclude_filtered = []
  for j in filtered:
    basename = os.path.basename(j)
    found = False
    for f in exclude_filters:
      if f.match(basename):
        found = True
        break
    if found:
      logging.debug("Ignoring JAR %s", j)
    else:
      exclude_filtered += [j]

  return exclude_filtered


def main():
  """Main function."""
  logging.basicConfig(level=logging.INFO)
  parser = argparse.ArgumentParser(
      description="Run Java API Compliance Checker.")
  parser.add_argument("-f", "--force-download",
                      action="store_true",
                      help="Download dependencies (i.e. Java JAVA_ACC) " +
                      "even if they are already present")
  parser.add_argument("-i", "--include-file",
                      action="append",
                      dest="include_files",
                      help="Regex filter for JAR files to be included. " +
                      "Applied before the exclude filters. " +
                      "Can be specified multiple times.")
  parser.add_argument("-e", "--exclude-file",
                      action="append",
                      dest="exclude_files",
                      help="Regex filter for JAR files to be excluded. " +
                      "Applied after the include filters. " +
                      "Can be specified multiple times.")
  parser.add_argument("-a", "--annotation",
                      action="append",
                      dest="annotations",
                      help="Fully-qualified Java annotation. " +
                      "Java ACC will only check compatibility of " +
                      "annotated classes. Can be specified multiple times.")
  parser.add_argument("--skip-clean",
                      action="store_true",
                      help="Skip cleaning the scratch directory.")
  parser.add_argument("--skip-build",
                      action="store_true",
                      help="Skip building the projects.")
  parser.add_argument("src_rev", nargs=1, help="Source revision.")
  parser.add_argument("dst_rev", nargs="?", default="HEAD",
                      help="Destination revision. " +
                      "If not specified, will use HEAD.")

  if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

  args = parser.parse_args()

  src_rev, dst_rev = args.src_rev[0], args.dst_rev

  logging.info("Source revision: %s", src_rev)
  logging.info("Destination revision: %s", dst_rev)

  # Construct the JAR regex patterns for filtering.
  include_filters = []
  if args.include_files is not None:
    for f in args.include_files:
      logging.info("Applying JAR filename include filter: %s", f)
      include_filters += [re.compile(f)]
  else:
    include_filters = [re.compile(".*")]

  exclude_filters = []
  if args.exclude_files is not None:
    for f in args.exclude_files:
      logging.info("Applying JAR filename exclude filter: %s", f)
      exclude_filters += [re.compile(f)]

  # Construct the annotation list
  annotations = args.annotations
  if annotations is not None:
    logging.info("Filtering classes using %d annotation(s):", len(annotations))
    for a in annotations:
      logging.info("\t%s", a)

  # Download deps.
  checkout_java_acc(args.force_download)

  # Set up the build.
  scratch_dir = get_scratch_dir()
  src_dir = os.path.join(scratch_dir, "src")
  dst_dir = os.path.join(scratch_dir, "dst")

  if args.skip_clean:
    logging.info("Skipping cleaning the scratch directory")
  else:
    clean_scratch_dir(scratch_dir)
    # Check out the src and dst source trees.
    checkout_java_tree(get_git_hash(src_rev), src_dir)
    checkout_java_tree(get_git_hash(dst_rev), dst_dir)

  # Run the build in each.
  if args.skip_build:
    logging.info("Skipping the build")
  else:
    build_tree(src_dir)
    build_tree(dst_dir)

  # Find the JARs.
  src_jars = find_jars(src_dir)
  dst_jars = find_jars(dst_dir)

  # Filter the JARs.
  src_jars = filter_jars(src_jars, include_filters, exclude_filters)
  dst_jars = filter_jars(dst_jars, include_filters, exclude_filters)

  if len(src_jars) == 0 or len(dst_jars) == 0:
    logging.error("No JARs found! Are your filters too strong?")
    sys.exit(1)

  run_java_acc(src_rev, src_jars,
               dst_rev, dst_jars, annotations)


if __name__ == "__main__":
  main()
