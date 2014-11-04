init -2:
    transform buffupnew(img):
        img
        alpha 1
        time 0.5
        linear 0.5 alpha 0
        
    transform delay_float_textnew(img,wait):
        img
        alpha 0
        time wait
        alpha 1
        
    transform warpoutnew(img):
        img
        alpha 0
        easein 1 alpha 1

screen battle_screen:
    tag tactical
    modal False
    zorder -5
    key "mousedown_4" action NullAction()#ZoomAction(["zoom", "in"])    #scroll in and out
    key "mousedown_5" action NullAction()#ZoomAction(["zoom", "out"])
    key "K_PAGEUP" action NullAction()#Return(["zoom", "in"])
    key "K_PAGEDOWN" action NullAction()#Return(["zoom", "out"])
    if 'mouseup_2' not in config.keymap['hide_windows']:
        key "mousedown_2" action Return(["next ship"])
    if 'mouseup_3' not in config.keymap['game_menu']:
        key "mousedown_3" action Return(["deselect"])
    key "]" action Return(["next ship"])
    key "[" action Return(["previous ship"])

    ##messing with the player for fun and profit
    if BM.battlemode:
        timer 900 repeat False action Show('game_over_gimmick')
    
    #add MouseTracker() #relates drags and clicks to the viewport and the BM

    if config.developer: #a release version should have set this to False
        key "Q" action Jump(['quit'])  ##DEBUG FAST QUIT##
        key "A" action Return(['anime'])
        if BM.phase != 'formation':
            key "P" action Return(['I WIN'])

    #$childx = round(3840*zoomlevel) #this makes it so you can't scroll past the edge of the battlefield when zoomed out
    #$childy = round(3006*zoomlevel+300) #extra 300 is so that the status window doesn't occlude ships in the far right bottom corner

    #$print "show screen"
    add BM.battle_bg xalign 0.5 yalign 0.5 #zoom 0.5 ##background for the battlefield##
    #add BattleScreen(zoomlevel, BM)
    add BattleScreen(BM)
    
##not part of the viewport##
    if BM.phase != 'formation':
        vbox:
            xalign 1.0
            vbox:
                xalign 1.0
                # textbutton "Battle Log" xalign 1.0 action Show('battle_log')
                # if BM.edgescroll == (0,0):
                    # textbutton "enable edgescroll" action SetField(BM,'edgescroll',(100,800*zoomlevel))
                # else:
                    # textbutton "disable edgescroll" action SetField(BM,'edgescroll',(0,0))
                # if BM.show_tooltips:
                    # textbutton "disable tooltips" xalign 1.0 action SetField(BM,'show_tooltips',False)
                # else:
                    # textbutton "enable tooltips"  xalign 1.0 action SetField(BM,'show_tooltips',True)
                
                if store.Difficulty < 3:
                    textbutton "restart turn" xalign 1.0 action Jump('restartturn')
    
            if config.developer:
                vbox:
                    # ypos 100
                    xalign 1.0
                    textbutton "Debug Cheats" xalign 1.0 action Return(['cheat'])
                    textbutton "Fast Quit" xalign 1.0 action Jump('quit')

                    if BM.debugoverlay:
                        textbutton "coord overlay" xalign 1.0 action SetField(BM,'debugoverlay',False)
                    else:
                        textbutton "coord overlay" xalign 1.0 action SetField(BM,'debugoverlay',True)
                    if BM.show_grid:
                        textbutton "new grid" xalign 1.0 action SetField(BM,'show_grid',False)
                    else:
                        textbutton "old grid" xalign 1.0 action SetField(BM,'show_grid',True)
                    textbutton "debug log" xalign 1.0 action Show('debug_window')

    if BM.just_moved:
        textbutton 'cancel movement':
            ypos 70
            text_size 50
            text_color 'fff'
            action Return(['cancel movement'])

    if not BM.showing_orders and not BM.order_used and not BM.missile_moving and not BM.moving and BM.phase == "Player" and sunrider.location != None:
        imagebutton:
            xpos 0
            ypos 0
            idle 'Battle UI/commandbar.png'
            hover hoverglow('Battle UI/commandbar.png')
            action [SetField(BM,'showing_orders',True),Show('orders')]
        text '{!s}'.format(BM.cmd):
            xanchor 1.0
            xpos 165
            ypos 10
            size 30
            color 'fff'
            outlines [(1,'000',0,0)]


    if BM.phase == 'Player':
        $endturnbutton_idle = im.MatrixColor('Battle UI/button_endturn.png',im.matrix.tint(0.6, 1.0, 0.5))
        for ship in player_ships:
            if ship.en >= ship.max_en:
                $endturnbutton_idle = im.MatrixColor('Battle UI/button_endturn.png',im.matrix.tint(1.0, 0.6, 0.5))
    
        imagebutton:
            xpos 90
            yalign 1.0
            idle endturnbutton_idle
            hover hoverglow(endturnbutton_idle)
            action Return(['endturn'])
            
            
    if BM.phase == 'formation':
        imagebutton:
            xpos 170
            yalign 1.0
            idle 'Skirmish/start.png'
            hover hoverglow('Skirmish/start.png')
            action [ If( BM.selected==None , Return(['start']) ) ]
            
        if BM.mission == 'skirmish':
            imagebutton:
                xpos 88
                ypos 690
                idle 'Skirmish/return.png'
                hover hoverglow('Skirmish/return.png')
                action Return(['quit'])
        
            $ idl = 'Skirmish/remove.png'
            if BM.remove_mode:
                $ idl = hoverglow(im.MatrixColor('Skirmish/remove.png',im.matrix.tint(1.0, 1.0, 0)))
            
            imagebutton:
                xpos 208
                ypos 759
                idle idl
                hover hoverglow('Skirmish/remove.png')
                action Return(['remove'])
                
            imagebutton:
                xpos 328
                ypos 828
                idle 'Skirmish/enemymusic.png'
                hover hoverglow('Skirmish/enemymusic.png')
                action Show('enemy_music')

            imagebutton:
                xpos 448
                ypos 897
                idle 'Skirmish/playermusic.png'
                hover hoverglow('Skirmish/playermusic.png')
                action Show('player_music')                 
        
init python:
    
    class BattleScreen(renpy.Displayable):
        
        def __init__(self, battlemanager, **kwargs):
            
            super(BattleScreen, self).__init__(**kwargs)
            
            self.BM = battlemanager #the battlemanager.  needed to get ship locations and ship actions
            self.oldst = None #helps keeps track of the time between frames
            self.buffposition = [[0 for i in xrange(GRID_SIZE[0]*GRID_SIZE[1])] for j in xrange(2)]
                #j index 0 is for the back buff image, j index 1 is for the front buff image
                #i index is the total number of spaces on the grid, so the array can accomodate any number of ships
                #the values stored keep track of how much time has elapsed since the buff started
            self.curseposition = [[0 for i in xrange(GRID_SIZE[0]*GRID_SIZE[1])] for j in xrange(2)]
                #works the same as buffposition
                #keeps track of curses
            self.floattextposition = [0 for i in xrange(GRID_SIZE[0]*GRID_SIZE[1])]
                #same as buffposition but no need for a two dimensional array
                #keeps track of time elapsed since the intercept text was first displayed
            self.missileposition = 0
                #same as buffposition but no need for a two dimensional array
                #keeps track of time elapsed since the missile was rendered on screen
            self.shipposition = 0
                #same as buffposition but no need for a two dimensional array
                #keeps track of time elapsed since the ship started moving
            self.mouse_has_moved = True
            self.rel = (0,0)
            
            self.BM.xadj = max(min(self.BM.xadj, round(3840*self.BM.zoomlevel-1920)), 0) #makes sure that scroll values are within limits when the battle starts
            self.BM.yadj = max(min(self.BM.yadj, round(3006*self.BM.zoomlevel+300-1080)), 0)
             
        def render(self, width, height, st, at):
            
            #dtime is the time between frames
            if self.oldst is None:
                self.oldst = st
            dtime = st - self.oldst
            self.oldst = st
            
            render = renpy.Render(width, height)
            
            #current_image = renpy.displayable(self.BM.battle_bg) #zoom 0.5 ##background for the battlefield##
            #child_render = renpy.render(current_image, width, height, st, at)
            #render.blit(child_render, (0, 0))
            
            
            def display_image(img, pos):
                #this function will only blit objects when they would be visible
                inrange = True
                image_width, image_height = child_render.get_size()
                posx, posy = pos
                posx -= self.BM.xadj
                posy -= self.BM.yadj
                pos = (posx, posy)
                
                if posx > config.screen_width or posx < 0 - image_width:
                    inrage = False
                    
                if posy > config.screen_height or posy < 0 - image_height:
                    inrange = False
                    
                if inrange:
                    render.blit(img, pos)
                    
                    renpy.redraw(self, 0)
                    
            def display_buff(img, pos, index, index2):
                #this function adjusts the position of the buff for every buffed ship
                posx, posy = pos
                posyf = int(posy - 190 * self.BM.zoomlevel)
                posynew = self.linear(1, self.buffposition[index][index2], posy, posyf)
                posy = posynew
                self.buffposition[index][index2] += dtime
                pos = posx, posy
                display_image(img, pos)
                
            def display_curse(img, pos, index, index2):
                #this function adjusts the position of the curse for every buffed ship
                posx, posy = pos
                posyf = int(posy + 190 * self.BM.zoomlevel)
                posynew = self.linear(1, self.curseposition[index][index2], posy, posyf)
                posy = posynew
                self.curseposition[index][index2] += dtime
                pos = posx, posy
                display_image(img, pos)
                
            def display_floattext(img, pos, wait, index):
                #this function adjusts the position of the intercept text
                delay = wait
                posx, posy = pos
                posyf = int(posy - 80 * self.BM.zoomlevel)
                posynew = self.easein(1, self.floattextposition[index] - delay, posy, posyf)
                posy = posynew
                pos = posx, posy
                if self.floattextposition[index] >= delay:
                    display_image(img, pos)
                self.floattextposition[index] += dtime
                
            def display_missile(img, posstart, posfinal, travel_time = .45):
                #this function adjusts the position of the flying missile
                posx, posy = posstart
                posxf, posyf = posfinal
                posxnew = self.linear(travel_time, self.missileposition, posx, posxf)
                posynew = self.linear(travel_time, self.missileposition, posy, posyf)
                posx = posxnew
                posy = posynew
                self.missileposition += dtime
                pos = posx, posy
                display_image(img, pos)
                
            def display_moveship(img, posstart, posfinal, travel_time = .45):
                #this function adjusts the position of the moving ship
                posx, posy = posstart
                posxf, posyf = posfinal
                posxnew = self.linear(travel_time, self.shipposition, posx, posxf)
                posynew = self.linear(travel_time, self.shipposition, posy, posyf)
                posx = posxnew
                posy = posynew
                self.shipposition += dtime
                pos = posx, posy
                display_image(img, pos)
                
            if self.BM.show_grid:
                for a in range(1,GRID_SIZE[0]+1):  #cycle through rows
                    for b in range(1,GRID_SIZE[1]+1):  #cycle through columns
                        xposition = dispx(a, b, self.BM.zoomlevel)
                        yposition = dispy(a, b, self.BM.zoomlevel)
                        xsize = int((HEXW + 4) * self.BM.zoomlevel)
                        ysize = int((HEXH + 4) * self.BM.zoomlevel)
                        
                        current_image = renpy.displayable('Battle UI/hex.png')
                        t = Transform(child = current_image, alpha = 0.4, size = (xsize, ysize))
                        child_render = renpy.render(t, width, height, st, at)
                        display_image(child_render, (xposition, yposition))
                        
            else:
                
                current_image = renpy.displayable('Battle UI/hexgrid.png')
                xpos = int(HEXW * self.BM.zoomlevel)
                ypos = int((HEXD-2) * self.BM.zoomlevel)
                xsize = int((HEXW+5.5) * self.BM.zoomlevel * 18)
                ysize = int((HEXD+4) * self.BM.zoomlevel * 16)
                #current_image = Image('Battle UI/hexgrid.png', alpha = 0.4, size = (xsize, ysize))  transform properties did not work when applied directly to the image.  No idea why
                t = Transform(child = current_image, alpha = 0.4, size = (xsize, ysize))
                child_render = renpy.render(t, width, height, st, at)
                display_image(child_render, (xpos, ypos))
            
            if not self.BM.hovered == None: #when you hover over a ship
                if self.BM.hovered.shield_generation > 0:
                    for a in range(1,GRID_SIZE[0]+1):  #cycle through rows
                        for b in range(1,GRID_SIZE[1]+1):  #cycle through columns
                            if get_distance(self.BM.hovered.location,(a,b)) <= self.BM.hovered.shield_range:
                                ship = self.BM.hovered
                                effective_shielding = ship.shield_generation + ship.modifiers['shield_generation'][0]
                                if effective_shielding > 0:
                                    xposition = dispx(a,b,self.BM.zoomlevel)
                                    yposition = dispy(a,b,self.BM.zoomlevel)
                                    xsize = int((HEXW + 4) * self.BM.zoomlevel)
                                    ysize = int((HEXH + 4) * self.BM.zoomlevel)
                                    
                                    current_image = renpy.displayable('Battle UI/blue hex.png')
                                    t = Transform(child = current_image, alpha = 0.7, size = (xsize, ysize))
                                    child_render = renpy.render(t, width, height, st, at)
                                    #print str(xposition) + " " + str(yposition)
                                    display_image(child_render, (xposition, yposition))
                                    
                if self.BM.hovered.flak > 0:
                    for a in range(1,GRID_SIZE[0]+1):  #cycle through rows
                        for b in range(1,GRID_SIZE[1]+1):  #cycle through columns
                            if get_distance(self.BM.hovered.location,(a,b)) <= self.BM.hovered.flak_range:
                                ship = self.BM.hovered
                                effective_flak = ship.flak + ship.modifiers['flak'][0]
                                if effective_flak > 0:
                                    xposition = dispx(a,b,self.BM.zoomlevel)
                                    yposition = dispy(a,b,self.BM.zoomlevel)
                                    xsize = int((HEXW + 4) * self.BM.zoomlevel)
                                    ysize = int((HEXH + 4) * self.BM.zoomlevel)
                                    
                                    current_image = renpy.displayable('Battle UI/red hex.png')
                                    t = Transform(child = current_image, alpha = 0.9, size = (xsize, ysize))
                                    child_render = renpy.render(t, width, height, st, at)
                                    display_image(child_render, (xposition, yposition))
                                    
            if not self.BM.weaponhover == None: #when you hover over a weapon button
                if self.BM.weaponhover.wtype == 'Missile' or self.BM.weaponhover.wtype == 'Rocket' or self.BM.weaponhover.name == 'Flak Off':
                    for a in range(1,GRID_SIZE[0]+1):  #cycle through rows
                            for b in range(1,GRID_SIZE[1]+1):  #cycle through columns
                                for ship in enemy_ships:
                                    if get_distance(ship.location,(a,b)) <= ship.flak_range:
                                        effective_flak = ship.flak + ship.modifiers['flak'][0]
                                        if effective_flak > 0:
                                            xposition = dispx(a,b,self.BM.zoomlevel)
                                            yposition = dispy(a,b,self.BM.zoomlevel)
                                            xsize = int((HEXW + 4) * self.BM.zoomlevel)
                                            ysize = int((HEXH + 4) * self.BM.zoomlevel)
                                            
                                            current_image = renpy.displayable('Battle UI/red hex.png')
                                            t = Transform(child = current_image, alpha = 0.9, size = (xsize, ysize))
                                            child_render = renpy.render(t, width, height, st, at)
                                            display_image(child_render, (xposition, yposition))
                                            
                if self.BM.weaponhover.wtype == 'Laser' or self.BM.weaponhover.wtype == 'Pulse' or self.BM.weaponhover.name == 'Shield Down' or self.BM.weaponhover.name == 'Shield Jam':
                    for a in range(1,GRID_SIZE[0]+1):  #cycle through rows
                            for b in range(1,GRID_SIZE[1]+1):  #cycle through columns
                                for ship in enemy_ships:
                                    if get_distance(ship.location,(a,b)) <= ship.shield_range:
                                        effective_shielding = ship.shield_generation + ship.modifiers['shield_generation'][0]
                                        if effective_shielding > 0:
                                            xposition = dispx(a,b,self.BM.zoomlevel)
                                            yposition = dispy(a,b,self.BM.zoomlevel)
                                            xsize = int((HEXW + 4) * self.BM.zoomlevel)
                                            ysize = int((HEXH + 4) * self.BM.zoomlevel)
                                            
                                            current_image = renpy.displayable('Battle UI/blue hex.png')
                                            t = Transform(child = current_image, alpha = 0.7, size = (xsize, ysize))
                                            child_render = renpy.render(t, width, height, st, at)
                                            display_image(child_render, (xposition, yposition))
                                            
            ## DISPLAY COVER ##
            for cover in self.BM.covers:
                xposition = dispx(cover.location[0],cover.location[1],self.BM.zoomlevel, 0.5)
                yposition = dispy(cover.location[0],cover.location[1],self.BM.zoomlevel, 0.5)
                xsize = int(210 * self.BM.zoomlevel)
                ysize = int(120 * self.BM.zoomlevel)
                
                current_image = renpy.displayable(cover.label)
                t = Transform(child = current_image, size = (xsize, ysize), rotate = cover.angle)
                child_render = renpy.render(t, width, height, st, at)
                image_width, image_height = child_render.get_size()
                display_image(child_render, (xposition - image_width * .5, yposition - image_height * .5))
                
                
            ## DISPLAY SHIP AVATARS ##
    
            for index, ship in enumerate(self.BM.ships): #cycle through every ship in the battle
                  ##first we show the circle base below every unit
                if ship.location != None:
                    xposition = dispx(ship.location[0],ship.location[1],self.BM.zoomlevel, 0.50 * ADJX) + int(self.BM.zoomlevel * MOVX)
                    yposition = dispy(ship.location[0],ship.location[1],self.BM.zoomlevel, 0.50 * ADJY) + int(self.BM.zoomlevel * MOVY)
                    xsize = int(210 * self.BM.zoomlevel)
                    ysize = int(120 * self.BM.zoomlevel)
                    if ship.faction == 'Player':
                        
                        current_image = renpy.displayable("Battle UI/player base.png")
                        t = Transform(child = current_image, size = (xsize, ysize))
                        child_render = renpy.render(t, width, height, st, at)
                        image_width, image_height = child_render.get_size()
                        display_image(child_render, (xposition - image_width * .5, yposition - image_height * .5))
                        
                    if ship.faction == 'PACT':
                        
                        current_image = renpy.displayable("Battle UI/pact_base.png")
                        t = Transform(child = current_image, size = (xsize, ysize))
                        child_render = renpy.render(t, width, height, st, at)
                        image_width, image_height = child_render.get_size()
                        display_image(child_render, (xposition - image_width * .5, yposition - image_height * .5))
                        
                    if ship.faction == 'Pirate':
                        
                        current_image = renpy.displayable("Battle UI/pirate_base.png")
                        t = Transform(child = current_image, size = (xsize, ysize))
                        child_render = renpy.render(t, width, height, st, at)
                        image_width, image_height = child_render.get_size()
                        display_image(child_render, (xposition - image_width * .5, yposition - image_height * .5))
                        
                    cell_width = 1920 / ((GRID_SIZE[0]+2)/2)
                    cell_height = 1503 / ((GRID_SIZE[1]+2)/2)
                        
                    xposition = dispx(ship.location[0],ship.location[1],self.BM.zoomlevel, 0.50 * ADJX) + int(self.BM.zoomlevel * MOVX)
                    yposition = dispy(ship.location[0],ship.location[1],self.BM.zoomlevel, 0.25 * ADJY) + int(self.BM.zoomlevel * MOVY)
                    
                    if ship.getting_buff:  #used if you buff someone
                        
                        current_image = renpy.displayable('Battle UI/buff_back.png')
                        t = Transform(child = current_image, zoom = (self.BM.zoomlevel/2.0))
                        t2 = buffupnew(t)
                        child_render = renpy.render(t2, width, height, st, at)
                        display_buff(child_render, (int(xposition-(cell_width/2) * self.BM.zoomlevel), yposition), 0, index)
                        
                    if not ship.getting_buff and self.buffposition[0][index] != 0:
                        self.buffposition[0][index] = 0
                    
                    if ship.getting_curse:  #used if you curse someone
                        current_image = renpy.displayable('Battle UI/curse_back.png')
                        t = Transform(child = current_image, zoom = (self.BM.zoomlevel/2.0))
                        t2 = buffupnew(t)
                        child_render = renpy.render(t2, width, height, st, at)
                        display_curse(child_render, (int(xposition-(cell_width/2) * self.BM.zoomlevel), yposition-(190) * self.BM.zoomlevel), 0, index)
                    
                    if not ship.getting_curse and self.curseposition[0][index] != 0:
                        self.curseposition[0][index] = 0
                        
                ## as of the new UI interact code (with MouseTracker) most of the following is defunct.
                ## only the parts that affect lbl do anything anymore.
            
                    #default values
                    mode = '' #default
                    lbl = ship.lbl
                    hvr = hoverglow(ship.lbl)

                #some properties of the imagebutton representing a ship change depending on circumstances
                    if ship.faction == 'Player':
                        #by default player ships can be selected, which the above values are already set to.

                        if self.BM.targetingmode:
                            #you cannot target yourself with an active weapon
                            mode = 'offline'

                            if self.BM.active_weapon.wtype == 'Support':
                                #except when the active weapon is a support skill. in that case, player ships become targets
                                mode = 'target'

                    else: #ship is an enemy faction
                        #by default enemy ships can be selected (to view stat details), which the above values are already set to.

                        if self.BM.targetingmode:
                            #with an active weapon selected enemies become targets
                            mode = 'target'

                            if self.BM.active_weapon.wtype == 'Melee' and (ship.stype != 'Ryder' or get_ship_distance(self.BM.selected,ship) != 1):
                                #except when the active weapon is melee and this enemy is neither a ryder nor next to the attacking ship
                                mode = 'offline'

                            if self.BM.active_weapon.wtype == 'Support':
                                mode = 'offline'

                    if self.BM.active_weapon != None:
                        if self.BM.active_weapon.name == 'Gravity Gun':
                            #the gravity gun is a bit unique
                            if ship.stype != 'Ryder':
                                mode = 'offline'
                            else:
                                mode = 'target'

                    if mode == 'target':
                        lbl = hoverglow(ship.lbl)
                    elif mode == 'offline':
                        lbl = im.MatrixColor(ship.lbl,im.matrix.brightness(-0.3))

                    if self.BM.hovered != None:
                        if self.BM.hovered == ship:
                            if mode != 'offline':
                                lbl = hoverglow(ship.lbl)
                            
                    current_image = renpy.displayable(lbl)
                    t = Transform(child = current_image, zoom = self.BM.zoomlevel/2.5)
                    child_render = renpy.render(t, width, height, st, at)
                    image_width, image_height = child_render.get_size()
                    display_image(child_render, (xposition - image_width * .5, yposition - image_height * .5))
                        
                    if ship.getting_buff:  #used if you buff someone
                        
                        current_image = renpy.displayable('Battle UI/buff_front.png')
                        t = Transform(child = current_image, zoom = (self.BM.zoomlevel/2.0))
                        t2 = buffupnew(t)
                        child_render = renpy.render(t2, width, height, st, at)
                        display_buff(child_render, (int(xposition - 96 * self.BM.zoomlevel), int(yposition + 50 * self.BM.zoomlevel)), 1, index)
                        
                    if not ship.getting_buff and self.buffposition[1][index] != 0:
                        self.buffposition[1][index] = 0
                    
                    if ship.getting_curse:  #used if you curse someone
                        current_image = renpy.displayable('Battle UI/curse_front.png')
                        t = Transform(child = current_image, zoom = (self.BM.zoomlevel/2.0))
                        t2 = buffupnew(t)
                        child_render = renpy.render(t2, width, height, st, at)
                        display_curse(child_render, (int(xposition - 96 * self.BM.zoomlevel), yposition-(190-50)* self.BM.zoomlevel), 1, index)
                        
                    if not ship.getting_curse and self.curseposition[1][index] != 0:
                        self.curseposition[1][index] = 0
                                
                        ##add the HP bar and the EN bar
                    if ship.faction == 'Player':
                        xposition = dispx(ship.location[0],ship.location[1],self.BM.zoomlevel,0.08 * ADJX) + int(self.BM.zoomlevel * MOVX)
                        yposition = dispy(ship.location[0],ship.location[1],self.BM.zoomlevel,0.66 * ADJY) + int(self.BM.zoomlevel * MOVY)
                        hp_size = int(405*(ship.max_hp))
                        
                        if float(ship.hp) > (ship.max_hp * 50 / 100):
                            current_image = renpy.displayable('Battle UI/label hp bar green.png')
                            t = Transform(child = current_image, zoom = (self.BM.zoomlevel/2.5), crop = (0,0,hp_size,79))
                            child_render = renpy.render(t, width, height, st, at)
                            display_image(child_render, (xposition, yposition))

                        if float(ship.hp) <= (ship.max_hp * 50 / 100) and float(ship.hp) > (ship.max_hp * 25 / 100):
                            current_image = renpy.displayable('Battle UI/label hp bar yellow.png')
                            t = Transform(child = current_image, zoom = (self.BM.zoomlevel/2.5), crop = (0,0,hp_size,79))
                            child_render = renpy.render(t, width, height, st, at)
                            display_image(child_render, (xposition, yposition))

                        if float(ship.hp) <= (ship.max_hp * 25 / 100):
                            current_image = renpy.displayable('Battle UI/label hp bar red.png')
                            t = Transform(child = current_image, zoom = (self.BM.zoomlevel/2.5), crop = (0,0,hp_size,79))
                            child_render = renpy.render(t, width, height, st, at)
                            display_image(child_render, (xposition, yposition))

                        xposition = dispx(ship.location[0],ship.location[1],self.BM.zoomlevel,0.08 * ADJX) + int(self.BM.zoomlevel * MOVX)
                        yposition = dispy(ship.location[0],ship.location[1],self.BM.zoomlevel,0.72 * ADJY) + int(self.BM.zoomlevel * MOVY)
                        energy_size = int(405*(float(ship.en)/ship.max_en))
                        
                        current_image = renpy.displayable('Battle UI/label energy bar.png')
                        t = Transform(child = current_image, zoom = (self.BM.zoomlevel/2.5), crop = (0,0,energy_size,79))
                        child_render = renpy.render(t, width, height, st, at)
                        display_image(child_render, (xposition, yposition))
                        
                        current_image = Text(str(ship.hp), size = int(20*self.BM.zoomlevel), font = "Font/sui generis rg.ttf", outlines = [(2,'000',0,0)])
                        child_render = renpy.render(current_image, width, height, st, at)
                        image_width, image_height = child_render.get_size()
                        display_image(child_render, (int(xposition+80*self.BM.zoomlevel) - image_width * .5, int(yposition+27*self.BM.zoomlevel) - image_height * .5))
                        
                    else:       #enemies

                        xposition = dispx(ship.location[0],ship.location[1],self.BM.zoomlevel,0.0675 * ADJX) + int(self.BM.zoomlevel * MOVX)
                        yposition = dispy(ship.location[0],ship.location[1],self.BM.zoomlevel,0.65 * ADJY) + int(self.BM.zoomlevel * MOVY)
                        hp_size = int(405*(ship.max_hp))
                        
                        if float(ship.hp) > (ship.max_hp * 50 / 100):
                            current_image = renpy.displayable('Battle UI/label hp bar enemy green.png')
                            t = Transform(child = current_image, zoom = (self.BM.zoomlevel/2.5), crop = (0,0,hp_size,120))
                            child_render = renpy.render(t, width, height, st, at)
                            display_image(child_render, (xposition, yposition))
                        
                        if float(ship.hp) <= (ship.max_hp * 50 / 100) and float(ship.hp) > (ship.max_hp * 25 / 100):
                            current_image = renpy.displayable('Battle UI/label hp bar enemy yellow.png')
                            t = Transform(child = current_image, zoom = (self.BM.zoomlevel/2.5), crop = (0,0,hp_size,120))
                            child_render = renpy.render(t, width, height, st, at)
                            display_image(child_render, (xposition, yposition))
                        
                        if float(ship.hp) <= (ship.max_hp * 25 / 100):
                            current_image = renpy.displayable('Battle UI/label hp bar enemy red.png')
                            t = Transform(child = current_image, zoom = (self.BM.zoomlevel/2.5), crop = (0,0,hp_size,120))
                            child_render = renpy.render(t, width, height, st, at)
                            display_image(child_render, (xposition, yposition))
                        
                        current_image = Text(str(ship.hp), size = int(20*self.BM.zoomlevel), font = "Font/sui generis rg.ttf", outlines = [(2,'000',0,0)])
                        child_render = renpy.render(current_image, width, height, st, at)
                        image_width, image_height = child_render.get_size()
                        display_image(child_render, (int(xposition+80*self.BM.zoomlevel) - image_width * .5, int(yposition+27*self.BM.zoomlevel) - image_height * .25))
                        
    ##show flak icon and intercept text
            if self.BM.missile_moving:
                for index, ship in enumerate(self.BM.ships):
                    if ship.flaksim != None and ship.flak > 0:
                        xposition = dispx(ship.location[0],ship.location[1],self.BM.zoomlevel,0.50 * ADJX) + int(self.BM.zoomlevel * MOVX)
                        yposition = dispy(ship.location[0],ship.location[1],self.BM.zoomlevel,0.25 * ADJY) + int(self.BM.zoomlevel * MOVY)
                        wait = ship.flaksim[0]
                        intercept_count = ship.flaksim[1]
                        if intercept_count:
                            self.BM.battle_log_insert(['attack', 'missile'], "{0} intercepted {1} missiles! Effectiveness: {2}%".format(ship.name, intercept_count, int(ship.flak_effectiveness)))
                            
                            
                        current_image = renpy.displayable('Battle UI/warning icon.png')
                        t = Transform(child = current_image, zoom = (self.BM.zoomlevel/2.5), alpha = 0.8)
                        t2 = delayed_image(wait, t)
                        child_render = renpy.render(t2, width, height, st, at)
                        image_width, image_height = child_render.get_size()
                        display_image(child_render, (xposition - image_width * .5, yposition - image_height * .5))

                        textcolor = 'f00'
                        if ship.faction == 'Player':
                            textcolor = '0f0'
                            
                        text = '{} intercepted! \neffectiveness: {}%'.format( intercept_count , int(ship.flak_effectiveness) )
                        current_image = Text(text, size = 28, color = textcolor, outlines = [(2,'000',0,0)])
                        t = delay_float_textnew(current_image, wait)
                        child_render = renpy.render(t, width, height, st, at)
                        image_width, image_height = child_render.get_size()
                        display_floattext(child_render, (xposition - image_width * .5, yposition - image_height * .5), wait, index)
                        
                if not self.BM.missile_moving and self.floattextposition[index] != 0:
                    self.floattextposition[index] = 0
                        
    ##show missiles on the map that are currently flying in space##

            if self.BM.missile_moving:
                for missile in self.BM.missiles:
                    if missile.parent.location != None and missile.target.location != None: #failsafes
                        xposition = dispx(missile.parent.location[0], missile.parent.location[1],self.BM.zoomlevel,0.50 * ADJX) + int(self.BM.zoomlevel * MOVX)
                        yposition = dispy(missile.parent.location[0], missile.parent.location[1],self.BM.zoomlevel,0.25 * ADJY) + int(self.BM.zoomlevel * MOVY)
                        next_xposition = dispx(missile.target.location[0],missile.target.location[1],self.BM.zoomlevel,0.50 * ADJX) + int(self.BM.zoomlevel * MOVX)
                        next_yposition = dispy(missile.target.location[0],missile.target.location[1],self.BM.zoomlevel,0.25 * ADJY) + int(self.BM.zoomlevel * MOVY)

                        travel_time = get_ship_distance(missile.parent,missile.target)*MISSILE_SPEED*1.5
                        
                        current_image = renpy.displayable(missile.lbl)
                        t = Transform(child = current_image, zoom = (self.BM.zoomlevel/4.0))
                        child_render = renpy.render(t, width, height, st, at)
                        image_width, image_height = child_render.get_size()
                        display_missile(child_render, (xposition - image_width * .5, yposition - image_height * .5), (next_xposition - image_width * .5, next_yposition - image_height * .5), travel_time)
                        
            if not self.BM.missile_moving and self.missileposition != 0:
                self.missileposition = 0
                
                    
##targeting window##

          ##if targeting mode is active show a targeting window over all enemy_ships that gives you chance to hit and other data
            if self.BM.weaponhover != None or self.BM.targetingmode and self.BM.selected != None:
                selected = self.BM.selected  #the screen sometimes loses track of self.BM.selected and crashes so a local is required

                for ship in self.BM.ships:
                    if ship.location != None:

                        if self.BM.weaponhover == None:
                            self.BM.weaponhover = self.BM.active_weapon
                        if self.BM.weaponhover.wtype == 'Support' and (ship.faction != 'Player' or self.BM.weaponhover.self_buff == True):
                            pass
                        elif self.BM.weaponhover.wtype != 'Support' and ship.faction == 'Player' and self.BM.weaponhover.wtype != 'Special':
                            # wtype:'Special' is a support type that's neither a curse nor a buff but can be used on enemies and player units both
                            pass
                        elif self.BM.weaponhover.wtype == 'Melee' and (ship.stype != 'Ryder' or get_ship_distance(ship,selected) > 1):
                            pass
                        
                        #the gravity gun is a little... special
                        if self.BM.weaponhover.name == 'Gravity Gun' and ship.stype != 'Ryder':
                            pass

                        xposition = dispx(ship.location[0],ship.location[1],self.BM.zoomlevel,0.75 * ADJX) + int(self.BM.zoomlevel * MOVX)
                        yposition = dispy(ship.location[0],ship.location[1],self.BM.zoomlevel,0.15 * ADJY) + int(self.BM.zoomlevel * MOVY)
                        
                        current_image = renpy.displayable('Battle UI/targeting_window.png')
                        t = Transform(child = current_image, zoom = self.BM.zoomlevel/1.3)
                        child_render = renpy.render(t, width, height, st, at)
                        image_width, image_height = child_render.get_size()
                        display_image(child_render, (xposition - image_width * .5, yposition - image_height * .5))
                        
                        xposition = dispx(ship.location[0],ship.location[1],self.BM.zoomlevel,.92 * ADJX) + int(self.BM.zoomlevel * MOVX)
                        yposition = dispy(ship.location[0],ship.location[1],self.BM.zoomlevel,.20 * ADJY) + int(self.BM.zoomlevel * MOVY)
                        
                        current_image = Text((str(ship.cth) + '%'), size = int(20*self.BM.zoomlevel), color = '000')
                        child_render = renpy.render(current_image, width, height, st, at)
                        image_width, image_height = child_render.get_size()
                        display_image(child_render, (xposition - image_width * .5, yposition - image_height * .5))
                    
                        xposition = dispx(ship.location[0],ship.location[1],self.BM.zoomlevel,0.75 * ADJX) + int(self.BM.zoomlevel * MOVX)
                        yposition = dispy(ship.location[0],ship.location[1],self.BM.zoomlevel,0.40 * ADJY) + int(self.BM.zoomlevel * MOVY)
                        if selected == None:  #workarounds
                            effective_flak = 0
                        else:
                            if self.BM.weaponhover.wtype == 'Rocket':
                                #this looks double but missile_eccm is from a ship through upgrades whereas weaponhover.eccm is rom the rocket itself. (default 10)
                                effective_flak = ship.flak + ship.modifiers['flak'][0] - selected.missile_eccm - self.BM.weaponhover.eccm
                            else:
                                effective_flak = ship.flak + ship.modifiers['flak'][0] - selected.missile_eccm

                        if effective_flak < 0:
                            effective_flak = 0
                        elif effective_flak > 100:
                            effective_flak = 100
                        
                        current_image = Text(str(effective_flak), size = int(14*self.BM.zoomlevel), color = 'fff')
                        child_render = renpy.render(current_image, width, height, st, at)
                        image_width, image_height = child_render.get_size()
                        display_image(child_render, (xposition - image_width * 1.0, yposition - image_height * .5))
                        
                        xposition = dispx(ship.location[0],ship.location[1],self.BM.zoomlevel,.92 * ADJX) + int(self.BM.zoomlevel * MOVX)
                        yposition = dispy(ship.location[0],ship.location[1],self.BM.zoomlevel,.40 * ADJY) + int(self.BM.zoomlevel * MOVY)
                        
                        current_image = Text(str(ship.shields), size = int(14*self.BM.zoomlevel), color = 'fff')
                        child_render = renpy.render(current_image, width, height, st, at)
                        image_width, image_height = child_render.get_size()
                        display_image(child_render, (xposition - image_width * 1.0, yposition - image_height * .5))
                        
                        xposition = dispx(ship.location[0],ship.location[1],self.BM.zoomlevel,1.0 * ADJX) + int(self.BM.zoomlevel * MOVX)
                        yposition = dispy(ship.location[0],ship.location[1],self.BM.zoomlevel,0.4 * ADJY) + int(self.BM.zoomlevel * MOVY)
                          ##when you hover over a weapon that does kinetic or assault type damage it shows you armor is double as effective
                        if self.BM.weaponhover == None:
                            weapon = self.BM.active_weapon
                        else:
                            weapon = self.BM.weaponhover
                        if weapon.wtype == 'Kinetic' or weapon.wtype == 'Assault':
                            current_image = Text((str(ship.armor) + 'x2'), size = int(12*self.BM.zoomlevel), color = 'fff')
                            child_render = renpy.render(current_image, width, height, st, at)
                            image_width, image_height = child_render.get_size()
                            display_image(child_render, (xposition, yposition - image_height * .5))
                            
                        else:
                            current_image = Text(str(ship.armor), size = int(14*self.BM.zoomlevel), color = 'fff')
                            child_render = renpy.render(current_image, width, height, st, at)
                            image_width, image_height = child_render.get_size()
                            display_image(child_render, (xposition, yposition - image_height * .5))
                        
                 ##DISPLAY MOVEMENT OPTIONS##
            if self.BM.selectedmode and self.BM.selected != None:
                if self.BM.selected.faction == 'Player' and not self.BM.targetingmode and not self.BM.phase == 'formation':
                    for tile in self.BM.selected.movement_tiles:
                        lbl = 'Battle UI/move_tile.png'
                        tile_location = (tile[1],tile[2])
                        xposition = dispx(tile[1],tile[2],self.BM.zoomlevel,0.5 * ADJX) + int(self.BM.zoomlevel * MOVX)
                        yposition = dispy(tile[1],tile[2],self.BM.zoomlevel,0.5 * ADJY) + int(self.BM.zoomlevel * MOVY)
                        
                        if 'player_ships' in globals() and 'enemy_ships' in globals(): #crashes upon existing battle if I don't do this   
                            if get_counter_attack(tile_location) and self.BM.selected.modifiers['stealth'][0] == 0:
                                lbl = im.MatrixColor(lbl,im.matrix.tint(1.0, 0.5, 0.5))
                        
                        if tile_location == self.BM.mouse_location:
                            lbl = hoverglow(lbl) 
                            
                        current_image = renpy.displayable(lbl)
                        t = Transform(child = current_image, alpha = 0.5, zoom = self.BM.zoomlevel * 0.2)
                        child_render = renpy.render(t, width, height, st, at)
                        image_width, image_height = child_render.get_size()
                        display_image(child_render, (xposition - image_width * .5, yposition - image_height * .5))
                        
                        current_image = Text((str(self.BM.selected.move_cost*tile[0]) + ' EN'), size = int(20*self.BM.zoomlevel), outlines = [(2,'000',0,0)])
                        child_render = renpy.render(current_image, width, height, st, at)
                        image_width, image_height = child_render.get_size()
                        display_image(child_render, (xposition - image_width * .5, yposition - image_height * .5))
                        
            if self.BM.vanguardtarget:   #creates buttons over enemy ships
                loc1 = sunrider.location
                loc2 = self.BM.mouse_location
                if get_distance(loc1, loc2) <= self.BM.vanguard_range:
                    tiles = interpolate_hex(loc1, loc2)
                    for i in tiles:
                        xposition = dispx(i[0],i[1],self.BM.zoomlevel)
                        yposition = dispy(i[0],i[1],self.BM.zoomlevel)
                        xsize = int((HEXW + 4) * self.BM.zoomlevel)
                        ysize = int((HEXH + 4) * self.BM.zoomlevel)
                        
                        current_image = renpy.displayable('Battle UI/vanguard hex.png')
                        t = Transform(child = current_image, alpha = 0.7, size = (xsize, ysize))
                        child_render = renpy.render(t, width, height, st, at)
                        display_image(child_render, (xposition, yposition))
                        
            if self.BM.enemy_vanguard_path is not None:
                for hex in self.BM.enemy_vanguard_path:
                    xposition = dispx(hex[0],hex[1],self.BM.zoomlevel)
                    yposition = dispy(hex[0],hex[1],self.BM.zoomlevel)
                    xsize = int((HEXW + 4) * self.BM.zoomlevel)
                    ysize = int((HEXH + 4) * self.BM.zoomlevel)
                    
                    current_image = renpy.displayable('Battle UI/vanguard hex.png')
                    t = Transform(child = current_image, alpha = 0.7, size = (xsize, ysize))
                    child_render = renpy.render(t, width, height, st, at)
                    display_image(child_render, (xposition, yposition))
                    
    #the Sunrider warps from one cell to another
            if self.BM.warping:
                for location in store.flash_locations:
                    xposition = dispx(location[0],location[1],self.BM.zoomlevel) + int(self.BM.zoomlevel * MOVX)
                    yposition = dispy(location[0],location[1],self.BM.zoomlevel,-0.5 * ADJY) + int(self.BM.zoomlevel * MOVY)
                    
                    current_image = renpy.displayable('Battle UI/label_warpflash.png')
                    t = Transform(child = current_image, zoom = (0.25 * self.BM.zoomlevel))
                    t2 = warpoutnew(t)
                    child_render = renpy.render(t2, width, height, st, at)
                    display_image(child_render, (xposition, yposition))

                ##MOVE SHIP FROM GRID TO GRID##
            if self.BM.moving and self.BM.selected != None:
                if self.BM.selected.current_location != None and self.BM.selected.next_location != None:
                    xposition = dispx(self.BM.selected.current_location[0],self.BM.selected.current_location[1],self.BM.zoomlevel,0.50 * ADJX) + int(self.BM.zoomlevel * MOVX)
                    yposition = dispy(self.BM.selected.current_location[0],self.BM.selected.current_location[1],self.BM.zoomlevel,0.25 * ADJY) + int(self.BM.zoomlevel * MOVY)
                    next_xposition = dispx(self.BM.selected.next_location[0],self.BM.selected.next_location[1],self.BM.zoomlevel,0.50 * ADJX) + int(self.BM.zoomlevel * MOVX)
                    next_yposition = dispy(self.BM.selected.next_location[0],self.BM.selected.next_location[1],self.BM.zoomlevel,0.25 * ADJY) + int(self.BM.zoomlevel * MOVY)

                    travel_time = self.BM.selected.travel_time

                    current_image = renpy.displayable(self.BM.selected.lbl)
                    t = Transform(child = current_image, zoom = (self.BM.zoomlevel/2.5))
                    child_render = renpy.render(t, width, height, st, at)
                    image_width, image_height = child_render.get_size()
                    display_moveship(child_render, (xposition - image_width * .5, yposition - image_height * .5), (next_xposition - image_width * .5, next_yposition - image_height * .5), travel_time)
                    
            if not self.BM.moving:
                self.shipposition = 0

            if self.BM.debugoverlay:  #may use this later for AI debug things too
                for a in range(1,GRID_SIZE[0]+1):  #cycle through rows
                    for b in range(1,GRID_SIZE[1]+1):  #cycle through columns
                        xposition = dispx(a,b,self.BM.zoomlevel,0.5 * ADJX) + int(self.BM.zoomlevel * MOVX)
                        yposition = dispy(a,b,self.BM.zoomlevel,0.5 * ADJY) + int(self.BM.zoomlevel * MOVY)
                        
                        current_image = Text('{}/{}'.format(a,b))
                        child_render = renpy.render(current_image, width, height, st, at)
                        image_width, image_height = child_render.get_size()
                        display_image(child_render, (xposition - image_width * .5, yposition - image_height * .5))
                        
            #edgescrolling
            if self.BM.edgescroll != (0,0):
                x,y = renpy.get_mouse_pos()
                if x < self.BM.edgescroll[0]:
                    self.BM.xadj = max(min(self.BM.xadj - self.BM.edgescroll[1]*dtime*self.BM.zoomlevel, round(3840*self.BM.zoomlevel-1920)), 0)
                    renpy.redraw(self, 0)
                if x > config.screen_width - self.BM.edgescroll[0]:
                    self.BM.xadj = max(min(self.BM.xadj + self.BM.edgescroll[1]*dtime*self.BM.zoomlevel, round(3840*self.BM.zoomlevel-1920)), 0)
                    renpy.redraw(self, 0)
                if y < self.BM.edgescroll[0]:
                    self.BM.yadj = max(min(self.BM.yadj - self.BM.edgescroll[1]*dtime*self.BM.zoomlevel, round(3006*self.BM.zoomlevel+300-1080)), 0)
                    renpy.redraw(self, 0)
                if y > config.screen_height - self.BM.edgescroll[0]:
                    self.BM.yadj = max(min(self.BM.yadj + self.BM.edgescroll[1]*dtime*self.BM.zoomlevel, round(3006*self.BM.zoomlevel+300-1080)), 0)
                    renpy.redraw(self, 0)
                        
            #renpy.redraw(self, 0)
            return render
            
        def per_interact(self):
            #should redraw only when needed
            renpy.redraw(self, 0)
        #    print "redraw"
        
        def event(self, ev, x, y, st):
            if (ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 4) or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_PAGEUP):
                self.BM.zoom_handling(["zoom", "in"])
                if self.BM.selectedmode: 
                    self.BM.selected.movement_tiles = get_movement_tiles(self.BM.selected)
                
            if (ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 5) or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_PAGEDOWN):
                self.BM.zoom_handling(["zoom", "out"])
                if self.BM.selectedmode: 
                    self.BM.selected.movement_tiles = get_movement_tiles(self.BM.selected)
            
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                self.mouse_has_moved = False
                self.rel = pygame.mouse.get_rel()
            
            if ev.type == pygame.MOUSEMOTION:
                self.mouse_has_moved = True
                renpy.hide_screen('game_over_gimmick')   #why this no werk?
                
                # if the left mouse button is pressed, it's a drag
                if ev.buttons[0] == 1:
                    if self.BM.draggable:
                        self.BM.xadj = max(min(self.BM.xadj - ev.rel[0] * 2, round(3840*self.BM.zoomlevel-1920)), 0)
                        self.BM.yadj = max(min(self.BM.yadj - ev.rel[1] * 2, round(3006*self.BM.zoomlevel+300-1080)), 0)
                        
                mouse_location = self.get_mouse_location()
                
                #vanguard targeting
                if self.BM.vanguardtarget:
                    if self.BM.mouse_location != mouse_location and ev.buttons[0] != 1:
                        if get_distance(sunrider.location,mouse_location) <= self.BM.vanguard_range:
                            self.BM.mouse_location = mouse_location
                            self.mouse_has_moved = True
                            #renpy.restart_interaction()
                
                
                #check for hovering over movement tiles
                if self.BM.selected != None:
                    if self.BM.mouse_location != mouse_location and ev.buttons[0] != 1:
                        if get_distance(self.BM.selected.location,mouse_location) <=4:
                            self.BM.mouse_location = mouse_location
                            self.mouse_has_moved = True
                            #renpy.restart_interaction()
                
                #check for hovering over ships
                if self.BM.hovered != None:
                    if self.BM.hovered.location != mouse_location:
                        self.BM.hovered = None
                        #renpy.restart_interaction()
                else:
                    for ship in self.BM.ships:
                        if ship.location == mouse_location:
                            self.BM.hovered = ship
                            #renpy.restart_interaction()
                            break
                            
            elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                # being very careful that the mouse -did not move- recently before an actual click is registered
                # otherwise it's a drag
                if not self.mouse_has_moved and pygame.mouse.get_rel() == (0,0):
                    # show_message('tried to click')
                    mouse_location = self.get_mouse_location()
                    
                    # if you are using short range warp or are in skirmish mode this is used
                    if self.BM.targetwarp:
                        if get_cell_available(mouse_location):
                            return ['warptarget',self.get_mouse_location()]
                    
                    #move handling
                    elif self.BM.selected != None and self.BM.weaponhover == None:
                        if self.BM.selected.faction == 'Player':
                            if get_cell_available(mouse_location):
                                distance = get_distance(self.BM.selected.location,mouse_location)
                                if distance <= 4:  #perhaps not really needed anymore?
                                    move_range = int(float(self.BM.selected.en) / self.BM.selected.move_cost)
                                    if distance <= move_range:
                                        return [ 'move' , mouse_location ]
                    
                    #sometimes it's possible to have nothing selected and still something left in self.BM.weaponhover
                    if self.BM.selected == None:
                        self.BM.weaponhover == None
                    
                    #selection handling
                    if (self.BM.weaponhover == None or self.BM.active_weapon != None) and not self.BM.targetwarp:
                        for ship in self.BM.ships:
                            if ship.location == mouse_location:
                                return ['selection',ship]
                            else:
                                pass
        
        def get_mouse_location(self):
            """
            get the mouse position and return the hex location the mouse is over.
            """
            a,b = renpy.get_mouse_pos()
            yoffset = 27 * self.BM.zoomlevel
            hexheight = HEXD * self.BM.zoomlevel
            hexwidth = HEXW * self.BM.zoomlevel
            # xmax,ymax = GRID_SIZE

            y = int( (b+self.BM.yadj-yoffset) / hexheight )
            if y%2==0:
                xoffset = hexwidth/2
            else:
                xoffset = 0
            x = int( (a+self.BM.xadj-xoffset) / hexwidth )
            return (x,y)
            
        #The interpolation functions are used for animating the images
        #       duration:  amount of time needed for the interpolation to finish
        #       elapsed:  the amount of time that hsa passed since the interpolation started
        #       svalue:  the starting value
        #       evalue:  the value to interpolate to
        
        def linear(self, duration, elapsed, svalue, evalue):
            elapsedclamp = min(elapsed, duration)
            fraction = elapsedclamp/duration
            distance = evalue - svalue
            finalvalue = svalue + (fraction * distance)
            return finalvalue
            
        def easein(self, duration, elapsed, svalue, evalue):
            elapsedclamp = min(elapsed, duration)
            fraction = elapsedclamp/duration
            distance = evalue - svalue
            finalvalue = svalue + (math.cos((1.0 - fraction) * math.pi / 2.0)) * distance
            return finalvalue
            
            
            
            
            
            
