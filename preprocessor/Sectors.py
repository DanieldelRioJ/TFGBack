"""
    def group_map_by_sectors(self):

        object_dict=self.object_dict.copy()
        self.object_dict={}
        for frame in object_dict:
            sector_matrix=[]
            for i in range(self.sectors_height//self.sector_size):
                sector_matrix.insert(i,[])
                for j in range(self.sectors_width//self.sector_size):
                    sector_matrix[i].insert(j,[])

            for appareance in object_dict.get(frame):
                sector_x1=appareance.col//self.sector_size
                sector_x2 = (appareance.col+appareance.w) // self.sector_size
                sector_y1 = appareance.row // self.sector_size
                sector_y2 = (appareance.row+appareance.h) // self.sector_size
                if(sector_x2>self.sectors_width):sector_x2=self.sectors_width-1
                if (sector_y2 > self.sectors_height): sector_y2 = self.sectors_height - 1
                try:
                    sector_matrix[sector_y1][sector_x1].append(appareance)
                    if sector_x2==sector_x1 and sector_y2==sector_y1:
                        continue
                    elif sector_x2!=sector_x1 and sector_y2 != sector_y1:
                        sector_matrix[sector_y2][sector_x2].append(appareance)
                        sector_matrix[sector_y1][sector_x2].append(appareance)
                        sector_matrix[sector_y2][sector_x1].append(appareance)
                        continue
                    else:
                        sector_matrix[sector_y2][sector_x2].append(appareance)
                except IndexError: #Happens when a gt box is partial outside the screen, so those points are not inside any sector
                    print(f"Error: id:{appareance.object.id} frame:{appareance.frame}, ({appareance.row},{appareance.col}),({appareance.row+appareance.w},{appareance.col+appareance.h})")
                    pass
            self.object_dict[frame]=sector_matrix

    def get_sectors(self,x1,y1,x2,y2):
        sectors=[]
        sector_x1 = x1 // self.sector_size
        sector_x2 = x2 // self.sector_size
        sector_y1 = y1 // self.sector_size
        sector_y2 = y2 // self.sector_size

        if sector_x2 > self.sectors_width: sector_x2 = self.sectors_width - 1
        if sector_y2 > self.sectors_height: sector_y2 = self.sectors_height - 1

        sectors.append((sector_y1,sector_x1))
        if sector_x2 != sector_x1 and sector_y2 != sector_y1:
            sectors.append((sector_y2, sector_x2))
            sectors.append((sector_y1, sector_x2))
            sectors.append((sector_y2, sector_x1))
        else:
            sectors.append((sector_y2, sector_x2))

        return sectors


    #It tell us if our empty square overlaps with any object considering also the margins and our sector
    def any_overlap_with_appearances_margins_in_our_sector(self,l1,r1,frame_appearances,margin_x=10,margin_y=10):

        for sector in self.get_sectors(l1.x,l1.y,r1.x,r1.y):
            try:
                for appearance in frame_appearances[sector[0]][sector[1]]:
                    row1, row2, col1, col2 = calculate_new_box(appearance, self.rows,self.cols, margin_x, margin_y)
                    if do_overlap(l1,r1,Point(col1,row1),Point(col2,row2)):
                        return True
            except IndexError:
                print(sector)
        return False"""

"""

#It tell us if our empty square overlaps with any object
def any_overlap(l1,r1,appearances):
    for appearance in appearances:
        if do_overlap(l1,r1,Point(appearance.col,appearance.row),Point(appearance.col+appearance.w,appearance.row+appearance.h)):
            return True
    return False

"""