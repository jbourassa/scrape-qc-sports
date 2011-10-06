require 'nokogiri'
require 'open-uri'
require 'CGI'
require 'net/http'
require 'JSON'

def getPosition(address)
  encodedAddress = CGI::escape(address + ', Quebec, QC')
  url = "http://maps.googleapis.com/maps/api/geocode/json?address=#{encodedAddress}&sensor=false"
  puts url
  response = Net::HTTP.get URI.parse(url)
  data = JSON.parse(response)
  location = data["results"][0]['geometry']['location']
  [location['lat'], location['lng']]
end

def cleanAddress(endroit)
  addressTags = endroit.next.next
  addressTags.xpath("span[@class='note']").unlink
  addressTags.content.gsub(/[\r\n\t]/, ' ').squeeze(' ').strip
end

def getTerrains
  doc = Nokogiri::HTML(open('http://www.ville.quebec.qc.ca/citoyens/loisirs_sports/tennis.aspx'))
  endroits = doc.xpath('//th[@headers="endroit"]')
  terrains = []
  endroits.each do |endroit| 
    name = endroit.content.gsub(/[\r\n\t]/, ' ').squeeze(' ').strip 
    address = cleanAddress(endroit)
    lat, lng = getPosition address
    terrains.push({ :name => name, :address => address, :lat => lat, :lng => lng })
  end
  terrains
end

terrains = getTerrains
terrains.each do |terrain| 
  puts terrain[:name] << ' lat: ' << terrain[:lat].to_s << ' lng: ' << terrain[:lng].to_s 
end
