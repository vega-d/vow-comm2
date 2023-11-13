#!/usr/bin/fish
echo "uploading" (ls *.py) "to" (ls /dev/ttyACM*)
for board in (ls /dev/ttyACM*)
  for file in (ls *.py)
    ampy -p $board put $file
  end
end