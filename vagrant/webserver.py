from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = "<html><body><h1>Restaurant List</h1><ul>"
                output += "<a href='/restaurants/new'>Create new restaurant</a>"
                restaurant_list = session.query(Restaurant).all()
                for r in restaurant_list:
                    output += '<li>%s' % r.name
                    output += '<br><a href="/restaurants/%s/edit">' % r.id
                    output += 'Edit</a><br><a href="/restaurants/%s/delete">' % r.id
                    output += 'Delete</a></li>'

                output += "</ul></body></html>"
                self.wfile.write(output)
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = "<html><body><h1>Create a new restaurant List</h1>"
                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>"
                output += "<label for='name'>Restaurant name:</label><br>"
                output += "<input id='name' name='name' type='text'><br><br><input type='submit' value='Create'></form>"
                output += "</body></html>"

                self.wfile.write(output)
            if self.path.endswith("/edit"):
                restaurant_id = self.path.split("/")[2]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                SelectedRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()

                output = "<html><body><h1>%s</h1>" % SelectedRestaurant.name
                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>" % SelectedRestaurant.id
                output += "<label for='newRestaurantName'>Restaurant name:</label><br>"
                output += "<input id='newRestaurantName' name='newRestaurantName' type='text'><br><br><input type='submit' value='Rename'></form>"
                output += "</body></html>"

                self.wfile.write(output)
            if self.path.endswith("/delete"):
                restaurant_id = self.path.split("/")[2]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = "<html><body><h1>Are you sure you want to delete?</h1>"
                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'>" % restaurant_id
                output += "<input type='submit' value='Yes'></form>"
                output += "</body></html>"

                self.wfile.write(output)

        except IOError:
            self.send_error(404, "File not found %s" % self.path)
    def do_POST(self):
        try:
            if self.path.endswith("restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)

                    restaurant_name = fields.get('name')[0]
                    print restaurant_name
                    new_restaurant = Restaurant(name = restaurant_name)
                    session.add(new_restaurant)
                    session.commit()

                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()

                output = "<html><body><h1>Create a new restaurant List</h1>"
                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>"
                output += "<label for='name'>Restaurant name:</label><br>"
                output += "<input id='name' name='name' type='text'><br><br><input type='submit' value='Create'></form>"
                output += "</body></html>"
                self.wfile.write(output)
                return
            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    restaurant_id = self.path.split("/")[2]
                    restaurant_name = fields.get('newRestaurantName')[0]

                    SelectedRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
                    if SelectedRestaurant != []:
                        SelectedRestaurant.name = restaurant_name
                        session.add(SelectedRestaurant)
                        session.commit()

                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()
            if self.path.endswith("/delete"):
                restaurant_id = self.path.split("/")[2]

                SelectedRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
                if SelectedRestaurant != []:
                    session.delete(SelectedRestaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
        except:
            pass
def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        print "Web server running on port %s" % port
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C pressed, stopping web server..."
        server.socket.close()

if __name__ == '__main__':
    main()
