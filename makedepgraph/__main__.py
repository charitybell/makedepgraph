import os
import subprocess
import sys
import tempfile
import typing as t
from collections import defaultdict
from dataclasses import dataclass

from dataclasses_json import DataClassJsonMixin, dataclass_json


@dataclass_json
@dataclass
class RemakeTarget(DataClassJsonMixin):
    name: str
    file: t.Optional[str]
    line: int
    start: float
    deps: t.Optional[list[str]]
    recipe: t.Optional[float]
    end: float
    depends: list[str]


@dataclass_json
@dataclass
class RemakeBuild(DataClassJsonMixin):
    version: str
    pid:  int
    creator: str
    argv: list[str]
    jobs: int
    server: bool
    status: str
    start: float
    end: float
    directory: str
    entry: list[str]
    targets: list[RemakeTarget]


builds = []
targets = defaultdict(list)

with tempfile.TemporaryDirectory() as tmpdir:
    subprocess.run(
        ['remake',
         '--profile=json',
         f'--profile-directory={tmpdir}',
         '--always-make',
         '--dry-run',
         *sys.argv[1:]],
        check=True,
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
    )

    for filename in os.listdir(tmpdir):
        with open(os.path.join(tmpdir, filename), 'r') as f:
            builds.append(RemakeBuild.from_json(f.read()))

print('digraph {')

for build in builds:
    for target in build.targets:
        targets[target.name].extend(target.depends)
        for depend in target.depends:
            print(f'"{target.name}" -> "{depend}";')

print('}')
