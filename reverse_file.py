import io


class ReversibleTextIOWrapper(io.TextIOWrapper):
    '''
    original from https://stackoverflow.com/a/23646049
    refactored to be OO
    '''
    
    
    def __init__(self, buffer, encoding=None, errors=None, newline=None, line_buffering=False, write_through=False, buf_size=8192):
        super().__init__(buffer, encoding, errors, newline, line_buffering, write_through)
        
        self.buf_size = buf_size
        self.reverse_readline_iterator = None
    
    def reverse_readline(self):
        if not self.reverse_readline_iterator:
            self.reverse_readline_iterator = self._reverse_readline_iter()
        
        return next(self.reverse_readline_iterator)
    
    def _reverse_readline_iter(self):
        segment = None
        offset = 0
        
        self.seek(0, io.SEEK_END)
        file_size = remaining_size = self.tell()
        
        while remaining_size > 0:
            offset = min(file_size, offset + self.buf_size)
            self.seek(file_size - offset)
            buffer = self.read(min(remaining_size, self.buf_size))
            remaining_size -= self.buf_size
            lines = buffer.split('\n')
            
            # the first line of the buffer is probably not a complete line so
            # we'll save it and append it to the last line of the next buffer
            # we read
            if segment is not None:
                # if the previous chunk starts right from the beginning of line
                # do not concact the segment to the last line of new chunk
                # instead, yield the segment first 
                if buffer[-1] is not '\n':
                    lines[-1] += segment
                else:
                    yield segment
            
            segment = lines[0]
            
            for index in range(len(lines) - 1, 0, -1):
                if len(lines[index]):
                    yield lines[index]
        
        # Don't yield None if the file was empty
        if segment is not None:
            yield segment
        
        self.reverse_readline_iterator = None
