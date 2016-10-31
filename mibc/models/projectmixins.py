
import os
import time
from datetime import datetime
from contextlib import contextmanager


class validation(object):
    
    _validation_status = None

    @contextmanager
    def _validation_store(self):
        path = os.path.join(self.path, ".mibc")
        if not os.path.exists(path):
            os.mkdir(path)

        fname = os.path.join(path, "validation.txt")
        try:
            f = open(fname, 'r+')
        except IOError:
            f = open(fname, 'w+')

        yield f
        f.close()

        
    @property
    def validation_status(self):
        """Returns the date and status (boolean) of the last validation run"""

        if self._validation_status is None:
            with self._validation_store() as validation_file:
                last_line = reduce( lambda last, current: current, 
                                    validation_file,
                                    None )
                if not last_line:
                    stamp, status = datetime.fromtimestamp(0), False
                else:
                    stamp, status = last_line.split("\t")
                    stamp = int(stamp)
                    stamp = datetime.fromtimestamp( int(stamp) )
                    status = bool( int(status) )
                self._validation_status = (stamp, status)

        return self._validation_status


    @validation_status.setter
    def validation_status(self, status_bool):
        with self._validation_store() as validation_file:
            # seek to the end of the file and save status
            validation_file.seek(0,2) 
            print >> validation_file, "%s\t%s" %( int(time.time()),
                                                  int(status_bool) )
